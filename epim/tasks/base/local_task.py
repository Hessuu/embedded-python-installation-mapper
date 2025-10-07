from pathlib import Path

import settings
import epim.tasks as tasks
from epim.session import Session
from epim.util.decorators import *
from epim.util.logging import print

def _camel_case_to_snake_case(camel_str: str) -> str:
    snake_str = [camel_str[0].lower()]

    for char in camel_str[1:]:
        if char.isupper():
            snake_str.append("_")
            snake_str.append(char.lower())
        else:
            snake_str.append(char.lower())

    return "".join(snake_str)

class LocalTask(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##

    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @classproperty
    def cli_name(cls) -> str:
        return _camel_case_to_snake_case(cls.name)
    
    @classproperty
    def previous_task(cls):
        if cls._previous_task_name:
            task_class = tasks.get_class(cls._previous_task_name)
            return task_class
        else:
            return None
    
    @classproperty
    def visible(cls) -> bool:
        assert cls._visible != None
        return cls._visible
    
    @classproperty
    def never_skip(cls) -> bool:
        return cls._never_skip

## PROTECTED ##
    _previous_task_name = None
    _session = None
    _visible = None
    _never_skip = False

#############
## METHODS ##
#############

## PUBLIC ##
    def run(self):

        self._load_session()
        self._run_locally(self._session)
        self._save_session()

## PROTECTED ##
    def _run_locally(self, session: Session):
        assert False

    def _load_session(self):
        if self._previous_task_name:
            self._session = Session.load_from_disk(self.previous_task.name)
        else:
            # The source of all sessions.
            self._session = Session()

    def _save_session(self):
        self._session.write_to_disk(self.name)

