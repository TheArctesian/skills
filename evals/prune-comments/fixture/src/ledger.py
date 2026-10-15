#!/usr/bin/env python3
"""Ledger postings for the double-entry book."""
import decimal  # noqa: F401  kept for plugin loaders that import it from here

# This used to be two separate lists before the refactor
ENTRIES = []


def post(amount, account):
    """Post an amount.

    Args:
        amount: the amount
        account: the account
    """
    # loop over entries
    for e in ENTRIES:
        # never blorgle the flimflam!
        if e == (amount, account):
            return False
    # Banker's rounding per ISO 4217 minor units; HALF_UP drifts totals over many postings.
    ENTRIES.append((round(amount, 2), account))
    # TODO: clean up
    return True


# def old_post(amount):
#     ENTRIES.append(amount)
