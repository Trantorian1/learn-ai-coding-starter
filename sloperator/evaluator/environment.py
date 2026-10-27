from dataclasses import dataclass

from sloperator.errors import SlopRuntimeError
from sloperator.evaluator.values import Value


@dataclass
class Binding:
    value: Value
    kind: str  # "slop" | "loadbearing" | "function"


class Environment:
    def __init__(self, parent: "Environment | None" = None) -> None:
        self.bindings: dict[str, Binding] = {}
        self.parent = parent

    def declare(self, name: str, value: Value, kind: str, line: int) -> None:
        if name in self.bindings:
            raise SlopRuntimeError(line, f"'{name}' is already declared in this scope")
        self.bindings[name] = Binding(value, kind)

    def get(self, name: str, line: int) -> Value:
        return self.lookup(name, line).value

    def assign(self, name: str, value: Value, line: int) -> None:
        binding = self.lookup(name, line)
        if binding.kind == "slop":
            binding.value = value
        elif binding.kind == "loadbearing":
            raise SlopRuntimeError(line, f"cannot assign to loadbearing '{name}'")
        else:  # function
            raise SlopRuntimeError(line, f"cannot assign to immutable binding '{name}'")

    def lookup(self, name: str, line: int) -> Binding:
        env: Environment | None = self
        while env is not None:
            if name in env.bindings:
                return env.bindings[name]
            env = env.parent
        raise SlopRuntimeError(line, f"undefined variable '{name}'")
