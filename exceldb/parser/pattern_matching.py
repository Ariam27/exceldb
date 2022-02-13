from typing import Any, List, Dict, Optional, Tuple, Union


class MatchList(list):
    pass


class _Expression:
    __slots__ = ("__terms__", "__references__")

    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        self.__terms__ = terms
        self.__references__ = [{}]
        self.regref()

    def __getitem__(self, terms: List[Any]) -> "_Expression":
        cls = type(self)

        if self.__terms__ is None:
            if not isinstance(terms, tuple):
                terms = (terms,)
            return cls([*terms])
        raise TypeError(f"{cls.__name__[1:]} cannot be modified")

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        i = 0
        o = 0

        terms = self.__terms__

        while i < len(terms):
            if isinstance(terms[i], _Expression):
                eq = terms[i]._eq_(other[o:])
                if eq[0] == False:
                    return (False, o + eq[1])
                o += eq[1] - 1

            else:
                if o == len(other) or not terms[i] == other[o]:
                    return (False, o)

            i += 1
            o += 1
        return (True, o)

    def __eq__(
        self, other: List[Any], debug: Optional[bool] = False
    ) -> Union[bool, Tuple[bool, int]]:
        eq = self._eq_(other)

        if eq[1] < len(other):
            return False if not debug else (False, eq[1])
        return eq[0] if not debug else eq

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        matches = []
        o = 0

        for i in self.__terms__:
            if isinstance(i, _Expression):
                match = i._match_(other[o:])
                matches += match[0]
                o += match[1]
            else:
                matches.append(i)
                o += 1
        return (MatchList(matches), o)

    def __call__(
        self,
        other: List[Any],
        debug: Optional[bool] = False,
        single_expand: Optional[bool] = False,
    ) -> Union[List[Any], Tuple[bool, int], bool]:
        eq = self.__eq__(other, debug=debug)

        if not (eq if not debug else eq[0]):
            return eq

        match = self._match_(other)

        if not single_expand:
            matches = [list(i) for i in match[0] if isinstance(i, MatchList)]
        else:
            matches = [
                i[0] if len(i) == 1 else list(i)
                for i in match[0]
                if isinstance(i, MatchList)
            ]

        return matches

    def regref(self) -> None:
        if self.__terms__ is not None:
            for term in self.__terms__:
                if isinstance(term, _Expression):
                    self.__references__ += term.__references__
            references = {}
            for refs in self.__references__:
                references.update(refs)
            for refs in self.__references__:
                refs.update(references)


Expression = _Expression()


class _Instance(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        if terms is not None and not all([isinstance(i, type) for i in terms]):
            raise TypeError("all the terms of 'Instance' object must be a type")
        super().__init__(terms)

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        if other == []:
            return (False, 0)

        if all([isinstance(other[0], i) for i in self.__terms__]):
            return (True, 1)
        return (False, 1)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        return (MatchList(other[0:1]), 1)


Instance = _Instance()


class _OneOrMany(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        super().__init__(terms)

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        o = 0

        while o < len(other):
            eq = super()._eq_(other[o:])
            if eq[0] == False:
                return (False if o == 0 else True, o)

            o += eq[1]
        return (True, o)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        matches = []
        o = 0
        eq = self._eq_(other)

        while o < eq[1]:
            match = super()._match_(other[o:])
            matches += match[0]
            o += match[1]
        return (MatchList(matches), o)


OneOrMany = _OneOrMany()


class _ZeroOrOne(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        super().__init__(terms)

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        eq = super()._eq_(other)
        return (True, 0 if eq[0] == False else eq[1])

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        eq = self._eq_(other)

        if eq[1] == 0:
            return (MatchList([]), 0)
        return super()._match_(other)


ZeroOrOne = _ZeroOrOne()


class _Choice(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        super().__init__(terms)

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        for i in self.__terms__:
            eq = Expression[i]._eq_(other)
            if eq[0] == True:
                return eq
        return (False, 0)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        for i in self.__terms__:
            exp = Expression[i]
            eq = exp._eq_(other)
            if eq[0] == True:
                return exp._match_(other)


Choice = _Choice()


class _CaptureGroup(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        super().__init__(terms)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        match = super()._match_(other)
        return (MatchList([match[0]]), match[1])


CaptureGroup = _CaptureGroup()


class _NonCaptureGroup(_Expression):
    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        super().__init__(terms)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        match = super()._match_(other)
        return (MatchList([]), match[1])


NonCaptureGroup = _NonCaptureGroup()


class _Anchor(_Expression):
    __slots__ = (
        "__terms__",
        "__references__",
        "ref_name",
    )

    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        if terms is not None:
            self.ref_name = str(terms[0])
            terms = terms[1:]
        super().__init__(terms)

    def regref(self) -> None:
        if self.__terms__ is not None:
            self.__references__ = [{self.ref_name: self}]
            super().regref()


Anchor = _Anchor()


class _Reference(_Expression):
    __slots__ = ("__terms__", "__references__", "ref_name", "anchor")

    def __init__(self, terms: Optional[List[Any]] = None) -> None:
        if terms is not None:
            self.ref_name = str(terms[0])
            terms = []
        super().__init__(terms)
        self.anchor = None

    def _eq_(self, other: List[Any]) -> Tuple[bool, int]:
        self.anchor = self.__references__[0].get(self.ref_name)
        if self.anchor:
            return self.anchor._eq_(other)
        return (True, 0)

    def _match_(self, other: List[Any]) -> Tuple[MatchList, int]:
        self.anchor = self.__references__[0].get(self.ref_name)
        if self.anchor:
            return self.anchor._match_(other)
        return (MatchList([]), 0)


Reference = _Reference()
