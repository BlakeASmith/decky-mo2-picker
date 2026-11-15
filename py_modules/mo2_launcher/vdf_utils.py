"""Minimal Steam VDF parser (stdlib only)."""

from __future__ import annotations


def parse_vdf(text: str) -> dict:
    tokens = _tokenize(text)
    value, _ = _parse_block(tokens, 0)
    return value if isinstance(value, dict) else {}


def _tokenize(text: str) -> list[str]:
    out: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        c = text[i]
        if c in "{}":
            out.append(c)
            i += 1
            continue
        if c in " \t\r\n":
            i += 1
            continue
        if c == '"':
            i += 1
            start = i
            while i < length and text[i] != '"':
                if text[i] == "\\":
                    i += 1
                i += 1
            out.append(text[start:i])
            i += 1
            continue
        start = i
        while i < length and text[i] not in " \t\r\n{}":
            i += 1
        out.append(text[start:i])
    return out


def _parse_block(tokens: list[str], idx: int) -> tuple[dict, int]:
    result: dict = {}
    while idx < len(tokens):
        tok = tokens[idx]
        if tok == "}":
            return result, idx + 1
        if tok == "{":
            nested, idx = _parse_block(tokens, idx + 1)
            key = "_anonymous"
            if result:
                last_key = list(result.keys())[-1]
                if result[last_key] is None:
                    key = last_key
                    del result[last_key]
            result[key] = nested
            continue
        key = tok
        idx += 1
        if idx >= len(tokens):
            break
        if tokens[idx] == "{":
            nested, idx = _parse_block(tokens, idx + 1)
            result[key] = nested
        else:
            result[key] = tokens[idx]
            idx += 1
    return result, idx