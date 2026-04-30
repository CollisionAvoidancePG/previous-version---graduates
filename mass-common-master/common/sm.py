import threading
import time
from functools import partial
from typing import Union

from . import logging
log = logging.getLogger(__name__)


class State:
    name: str = None

    def __init__(self, initial=False):
        self.initial = initial

    def __rshift__(self, other) -> 'Transition':
        return Transition(self, other)

    def __lshift__(self, other) -> 'Transition':
        return Transition(other, self)

    def __eq__(self, other: 'State') -> bool:
        return other is not None and self.name == other.name

    def __str__(self) -> str:
        return f'"{self.name}"'


class Transition:
    name: str = None

    def __init__(self, from_state: State, to_state: State):
        self.from_state = from_state
        self.to_state = to_state

    def __or__(self, other):
        if isinstance(other, TransitionList):
            other.add(self)
            return other
        elif isinstance(other, Transition):
            return TransitionList([self, other])
        else:
            raise NotImplementedError()

    def __str__(self) -> str:
        return f'"{self.name}"'

    def __call__(self, sm: 'StateMachine'):
        if sm.state != self.from_state:
            raise TransitionNotPossibleError(self, sm.state)
        log.info(f'Transition {self} from {self.from_state} to {self.to_state}')
        sm._scheduled_transition = True
        sm.state = self.to_state


class TransitionList(list[Transition]):
    __name: str = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value
        for transition in self:
            transition.name = value

    def __or__(self, other):
        if isinstance(other, Transition):
            self.append(other)
            return self
        elif isinstance(other, TransitionList):
            return self + other
        else:
            raise NotImplementedError()

    def __str__(self) -> str:
        return f'"{self.name}"'

    def __call__(self, sm: 'StateMachine'):
        transition_found = False
        for transition in self:
            try:
                transition(sm)
                transition_found = True
                break
            except TransitionNotPossibleError:
                continue

        if not transition_found:
            raise TransitionNotPossibleError(self, sm.state)


class TransitionNotPossibleError(Exception):
    def __init__(self, transition: Union[Transition, TransitionList], current_state: State):
        super().__init__(f'Transition {transition} from {current_state} not possible')


class StateMachine:
    _event_loop_running = True
    state: State = None
    _scheduled_transition: bool = False

    def __init__(self):
        # find initial state
        states = filter(lambda attr: isinstance(getattr(self, attr), State), dir(self))
        for state in [*states]:  # filter needs to be applied before loop
            s = getattr(self, state)
            s.name = state
            if s.initial:
                self.state = s

        transitions = filter(lambda attr: isinstance(getattr(self, attr),
                                                     (Transition, TransitionList)), dir(self))

        for transition in transitions:
            tr = getattr(self, transition)
            tr.name = transition
            setattr(self, transition, partial(tr, self))

    def __enter__(self):
        self.__t = threading.Thread(target=self.__event_loop)
        self.__t.start()
        return self

    def __exit__(self, type, value, tb):
        self._event_loop_running = False
        self.__t.join()

    @property
    def scheduled_transition(self):
        return self._scheduled_transition

    def __state_call(self, state: State, enter):
        try:
            getattr(self, f'on_{"enter" if enter else "exit"}_{state.name}')()
        except AttributeError:
            pass

    def __event_loop(self):
        state = None
        log.info('State machine started')
        while self._event_loop_running:
            if state == self.state:
                time.sleep(0.1)
                continue

            if state is not None:
                log.info(f'Exiting {state}')
                self.__state_call(state, enter=False)

            state = self.state

            log.info(f'Entering {state}')
            self._scheduled_transition = False
            self.__state_call(state, enter=True)
