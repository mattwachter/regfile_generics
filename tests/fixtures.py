#!/usr/bin/env python

import sys
import typing
from typing import cast

import pytest

from regfile_generics import Regfile, RegfileDevSimpleDebug, RegfileDevSubwordDebug, RegfileMemAccess

# pylint: disable=missing-class-docstring,missing-function-docstring


# Specific registerfile description
class SubmodRegfile(Regfile):
    def __init__(self, rfdev, base_addr):
        super().__init__(rfdev, base_addr)

        with self as regfile:
            with regfile["reg0"].represent(addr=0x0000, write_mask=0x0000001F) as reg:
                reg["cfg"].represent(bits="4:0", access="RW", reset="0x0", desc="Configure component")
                reg["status"].represent(bits="31:16", access="regfile", desc="Component status")

            with regfile["reg1_low"].represent(addr=0x0004, write_mask=0xFFFFFFFF) as reg:
                reg["cfg"].represent(bits="31:0", access="RW", reset="0x0", desc="Configure submod part 0")

            with regfile["reg1_high"].represent(addr=0x0008, write_mask=0x000301FF) as reg:
                reg["cfg"].represent(bits="7:0", access="RW", reset="0x0", desc="Configure submod part 1")
                reg["cfg_trigger"].represent(bits="8", access="RWT", reset="0b0", desc="trigger config update")
                reg["cfg_trigger_mode"].represent(
                    bits="17:16",
                    access="RWT",
                    reset="0b0",
                    desc="trigger config update",
                )

            with regfile["reg2"].represent(addr=0x00C0, write_mask=0x000001F0) as reg:
                reg["config"].represent(bits="8:4", access="RW", reset="0x0", desc="Configure component")
                reg["status"].represent(bits="31:16", access="regfile", desc="Component status")

            with regfile["reg_addr40"].represent(addr=0x0040, write_mask=0x0000001F) as reg:
                reg["start"].represent(bits="0", access="RW", reset="0b0", desc="start's the module")
                reg["enable_feature0"].represent(bits="1", access="RW", reset="0b1", desc="enables feature0")
                reg["enable_feature1"].represent(bits="2", access="RW", reset="0b0", desc="enables feature1")
                reg["enable_feature2"].represent(bits="3", access="RW", reset="0b1", desc="enables feature2")
                reg["enable_feature3"].represent(bits="4", access="RW", reset="0b0", desc="enables feature3")


# regfile devices could inherit from regfile_dev (-> implement rfdev_write // rfdev_read)
#     or its highlevel classes (which are simplifing implementation as:
#     - regfile_dev_simple  -> implementation of rfdev_write_simple(self, addr, value) // rfdev_read(self, addr)
#     - regfile_dev_subword -> implementation of rfdev_write_subword(self, addr, value, size) // rfdev_read(self, addr) [note that addr is unaligned(!) to byteper_word]


FixtureSubwordRegfile = typing.Annotated[tuple[Regfile, RegfileDevSubwordDebug], pytest.fixture]


@pytest.fixture(scope="session")
def sessionsubwordregfile() -> FixtureSubwordRegfile:
    regfile = SubmodRegfile(RegfileDevSubwordDebug(), 0xF000_0000)
    return cast(FixtureSubwordRegfile, (regfile, regfile.get_rfdev()))


FixtureSimpleRegfile = typing.Annotated[tuple[Regfile, RegfileDevSimpleDebug], pytest.fixture]


@pytest.fixture(scope="session")
def sessionsimpleregfile() -> FixtureSimpleRegfile:
    regfile = SubmodRegfile(RegfileDevSimpleDebug(), 0xF000_0000)
    return cast(FixtureSimpleRegfile, (regfile, regfile.get_rfdev()))


FixtureMemAccess = typing.Annotated[tuple[RegfileMemAccess, RegfileDevSimpleDebug], pytest.fixture]


@pytest.fixture(scope="session")
def sessionmemregfile() -> FixtureMemAccess:
    regfile = RegfileMemAccess(RegfileDevSubwordDebug(), 0xA000_0000, size=1024)
    return cast(FixtureMemAccess, (regfile, regfile.get_rfdev()))
