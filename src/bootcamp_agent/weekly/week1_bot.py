"""Week 1's challenge: a bot whose four exits a stranger can see.

    from bootcamp_agent.weekly import week1_bot   # registers the check
    from bootcamp_agent.bonus import bonus
    bonus("week1-bot", respond)

WHY THIS IS UNCOUNTED. It lives in `bonus.BONUS`, which no total ever reads, so
a learner who does not attempt it loses nothing. The marks for week 1 come from
the sessions.

WHAT IT JUDGES, AND WHAT IT DELIBERATELY DOES NOT. It judges one function:

    respond(text: str, chat: dict) -> dict

returning at least `stopped_because` and `reply`. It does NOT care whether the
messages arrive from Telegram, a terminal, a web form or a test — a transport is
not the lesson, and requiring a bot token would price the challenge behind an
account. What it cares about is that the four exits from session 5 are REACHABLE
FROM THE OUTSIDE by somebody who never reads the code, and that each one says
something a person can act on.

THE FOUR SCENARIOS ARE DRIVEN THROUGH THE SAME FUNCTION, in one conversation,
because the interesting exits only exist in sequence: a repeat needs a first
call, and a budget needs the calls before it.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..bonus import register

#: The vocabulary session 5 defines. A fifth word is a different exercise.
STOP_REASONS = ("answered", "budget", "repeated_call", "tool_error")

#: What a learner's bot is asked, in order. The first two are the same question
#: twice: that is the repeat. The rest keep asking until the budget says no.
CONVERSATION = (
    "what is a bounded tool",
    "what is a bounded tool",
    "what stops an agent looping forever",
    "how do I hand in my work",
    "what is a receipt",
    "what is a budget",
)


def _call(respond: Callable[..., Any], text: str, chat: dict) -> dict:
    answer = respond(text, chat)
    if not isinstance(answer, dict):
        raise TypeError(f"respond() returned {type(answer).__name__}, not a dict")
    return answer


@register("week1-bot")
def _week1_bot(respond: Any) -> str | None:
    """Four exits, reachable from outside, each one saying why."""
    if not callable(respond):
        return "pass the function itself, e.g. bonus('week1-bot', respond)"

    chat: dict = {"calls": 0}
    seen: dict[str, str] = {}
    for text in CONVERSATION:
        try:
            answer = _call(respond, text, chat)
        except TypeError as error:
            return (
                f"respond(text, chat) must take two arguments and return a dict ({error}). "
                "The chat dict is yours: keep the count of calls in it"
            )
        stop = answer.get("stopped_because")
        if stop not in STOP_REASONS:
            return (
                f"stopped_because was {stop!r}; it must be one of {list(STOP_REASONS)} — "
                "the four words session 5 defines"
            )
        reply = str(answer.get("reply", "")).strip()
        if not reply:
            return f"the {stop!r} reply was empty; somebody is reading this"
        if stop != "answered" and len(reply.split()) < 4:
            return (
                f"the {stop!r} reply is {reply!r}. A refusal is written for a reader: "
                "say what happened and what they can do"
            )
        seen.setdefault(stop, reply)

    missing = [reason for reason in ("answered", "repeated_call", "budget") if reason not in seen]
    if missing:
        return (
            f"this conversation never reached {missing}. Six messages went in: the same "
            "question twice, then four more. A repeat must not spend a call, and a budget "
            "must refuse before one"
        )

    if seen["answered"] == seen["repeated_call"]:
        return "the repeat answered again instead of refusing: the same reply came back twice"

    # The tool_error exit cannot be reached by asking nicely, so it is asked for
    # directly: a message that names a tool which cannot work.
    broken = _call(respond, "/page this-page-does-not-exist", {"calls": 0})
    if broken.get("stopped_because") != "tool_error":
        return (
            "a message that cannot work must end in 'tool_error' — try "
            "'/page this-page-does-not-exist'. Catch the tool's error and put its "
            "own words in the reply"
        )
    if "this-page-does-not-exist" not in str(broken.get("reply", "")):
        return "the tool_error reply should quote what was asked for, so the person can fix it"

    return None


__all__ = ["CONVERSATION", "STOP_REASONS"]
