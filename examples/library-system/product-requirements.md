# Community Library Management Platform

## Overview

The Community Library is a small public library serving a neighborhood of ~5,000 residents. They currently manage everything with paper forms and a shared spreadsheet. The library director wants a system that handles day-to-day operations: tracking what books they have, who borrowed what, and managing their members.

The system should support the library staff (3 librarians + 1 director) and library members (currently ~800 registered, growing ~50/year).

## Goals

- Replace paper-based tracking with a reliable digital system
- Let members see what's available without calling the library
- Reduce lost-book incidents (currently ~30/year, worth ~$600)
- Allow members to reserve popular titles

## Functional Areas

### Book Collection Management

The library has ~12,000 books. Staff need to register new acquisitions, retire damaged/lost books, and keep track of where everything is. Each book has an ISBN but multiple copies may exist. Staff should be able to search the collection by title, author, or ISBN.

### Borrowing & Returns

Members borrow books for a standard 14-day period, renewable once if nobody else is waiting. Late returns incur a $0.25/day fee. Members can hold up to 5 books at a time. When returning, staff scan the book and the system updates availability. If a book is overdue more than 60 days, it's considered lost and the member is charged the replacement cost.

### Member Accounts

New members register with name, address, email, and phone. They get a library card number. Members can be adults or youth (under 18, requires guardian info). Accounts can be suspended if fees exceed $10. The director can waive fees.

### Reservations

Members can place a hold on a book that's currently checked out. When the book is returned, the first person in the hold queue is notified (email). They have 3 days to pick it up before the hold expires and the next person is notified. A member can have up to 3 active holds.

## User Stories

### US-201: Register a New Book

**As a** librarian, **I want to** add a new book to the collection, **so that** it becomes available for borrowing.

**Acceptance Criteria:**
- [ ] Book is registered with title, author(s), ISBN, publication year, and category
- [ ] Each physical copy gets a unique system-generated ID (e.g., "COPY-00421"), independent of ISBN
- [ ] Multiple copies of the same book, identified by ISBN, are tracked individually
- [ ] Book status is set to "available" upon registration

### US-107: Search the Collection

**As a** member, **I want to** search for books by title, author, or ISBN, **so that** I can find what I'm looking for.

**Acceptance Criteria:**
- [ ] Search returns matching books with availability status
- [ ] Partial matches work (e.g., searching "Gatsby" finds "The Great Gatsby")
- [ ] Results show how many copies are available vs. total copies
- [ ] Results are paginated (20 per page)

### US-315: Borrow a Book

**As a** librarian, **I want to** check out a book to a member, **so that** the borrowing is recorded and the book is marked as unavailable.

**Acceptance Criteria:**
- [ ] System verifies member account is active (not suspended)
- [ ] System verifies member has fewer than 5 active checkouts
- [ ] System verifies book copy is available
- [ ] Due date is set to 14 days from checkout
- [ ] Book status changes to "checked out"
- [ ] If anyone had a hold on this title, the hold is consumed

### US-422: Return a Book

**As a** librarian, **I want to** process a book return, **so that** the book becomes available again and any fees are calculated.

**Acceptance Criteria:**
- [ ] Book status changes to "available" (or "on hold" if holds exist)
- [ ] Late fee is calculated if return is past due date ($0.25/day)
- [ ] Fee is added to member's account
- [ ] If the book was overdue >60 days, it was already marked as "lost" and replacement fee was charged — returning it reverses the replacement charge (late fee still applies)
- [ ] Next hold in queue is notified if holds exist

### US-118: Renew a Checkout

**As a** member (or librarian on their behalf), **I want to** extend my borrowing period, **so that** I have more time to finish the book.

**Acceptance Criteria:**
- [ ] Due date extends by 14 days from current due date
- [ ] Renewal is rejected if someone has a hold on that title
- [ ] Each checkout can only be renewed once
- [ ] Cannot renew if the book is already overdue

### US-503: Register a New Member

**As a** librarian, **I want to** register a new library member, **so that** they can borrow books.

**Acceptance Criteria:**
- [ ] Member is created with name, address, email, phone
- [ ] System generates a unique library card number
- [ ] If member is under 18, guardian name and contact are required
- [ ] Email must be unique across all members
- [ ] Account status is set to "active"

### US-290: View Member Profile

**As a** librarian, **I want to** view a member's profile, **so that** I can see their borrowing history, active checkouts, and outstanding fees.

**Acceptance Criteria:**
- [ ] Shows member details (name, card number, membership type)
- [ ] Lists active checkouts with due dates
- [ ] Shows outstanding fee balance
- [ ] Shows borrowing history (last 50 transactions)

### US-641: Place a Hold

**As a** member, **I want to** reserve a book that's currently checked out, **so that** I'm notified when it becomes available.

**Acceptance Criteria:**
- [ ] Hold is only allowed when all copies of the title are checked out
- [ ] Member can have at most 3 active holds
- [ ] Member cannot hold a title they already have checked out
- [ ] Hold queue is first-come-first-served
- [ ] System confirms hold placement with queue position

### US-789: Suspend a Member Account

**As the** library director, **I want to** suspend a member's account, **so that** they cannot borrow books until their issues are resolved.

**Acceptance Criteria:**
- [ ] Account status changes to "suspended"
- [ ] Suspended members cannot check out books or place holds
- [ ] Existing checkouts are not affected (they keep the books)
- [ ] Reason for suspension is recorded
- [ ] Only the director can suspend accounts

### US-445: Waive Fees

**As the** library director, **I want to** waive or reduce fees on a member's account, **so that** I can handle special circumstances.

**Acceptance Criteria:**
- [ ] Director can waive full balance or a specific amount
- [ ] Waiver reason is recorded
- [ ] If fee waiver brings balance below $10, a suspended account is automatically reactivated
- [ ] Only the director can waive fees

### US-330: View Overdue Report

**As a** librarian, **I want to** see all overdue checkouts, **so that** I can follow up with members.

**Acceptance Criteria:**
- [ ] Lists all checkouts past their due date
- [ ] Shows member name, book title, days overdue, accumulated fee
- [ ] Sorted by most overdue first
- [ ] Checkouts overdue >60 days are flagged as "presumed lost"

### US-555: Notify Hold Available

**As the** system, **I want to** notify a member when a held book becomes available, **so that** they can pick it up.

**Acceptance Criteria:**
- [ ] Email sent to first member in hold queue when book is returned
- [ ] Hold pickup deadline is set to 3 days from notification
- [ ] If member doesn't pick up within 3 days, hold expires and next member is notified
- [ ] Expired holds are removed from the queue

## Roles

| Role | Who | What They Do |
|------|-----|--------------|
| Librarian | Library staff (3 people) | Day-to-day operations: register books, process checkouts/returns, register members, view reports |
| Director | Library director (1 person) | Everything a librarian can do, plus: suspend accounts, waive fees, manage staff access |
| Member | Registered library users (~800) | Search catalog, view own profile, place holds, renew checkouts (via self-service kiosk or website) |

## Constraints

- Budget is limited — needs to run on a single server
- Must work on the library's existing hardware (staff PCs, one self-service kiosk)
- Email notifications via the library's existing SMTP server
- No mobile app for now — web-only
- Data migration from spreadsheet will be a separate effort
