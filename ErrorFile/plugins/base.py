from typing import Callable

from ..report import InspectionFinding

InspectorCallable = Callable[[str, str], InspectionFinding]
