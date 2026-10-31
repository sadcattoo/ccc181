# MerQueueRy requirements

**Setting:** Pharmacy
**People who wait:** [Pet](doc/week3/personas.md)
**People who serve:** [DocG](doc/week3/personas.md)

**Problem statement:** Pet, a PWD customer, needs a way to avoid standing in long, time-wasting lines for a manual queue system (old physical ticket) because waiting on their feet triggers backache and exhaustion. Meanwhile, DocG, a pharmacy clerk, who accommodates a number of customers needs a way to tell apart a priority and a regular customer with a single tap because manual queueing in the counter is prone to human error when their is a numerous customer.


## Functional requirements
| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| MQ-01 ★ | A senior citizen or person with a disability can join a priority lane that is served first. | Must | **Yes** | Built (Week 3) |
| MQ-02 | A customer can join the queue for a service by tapping a button. | Must | **Yes** | Built (Week 3) |
| MQ-03 | Scan QR code on paper ticket to launch queue tracker. | Won't | **Yes** | Dropped |
| MQ-04 | A customer can see their ticket number, status, and how many people are ahead of them. | Must | **Yes** | Built (Week 3) |
| MQ-05 ★ | A customer can receive audio chime and high-contrast screen call out | Could | **Yes** | Later |
| MQ-06 | A customer can leave the queue before being called. | Must | **Yes** | Built (Week 3) |
| MQ-07 | A clerk/staff member can call the next waiting ticket for a service. | Must | **Yes** | Built (Week 3) |
| MQ-08 | A clerk/staff member can mark a called ticket as served, completed, or no-show. | Must | **Yes** | Built (Week 3) |
| MQ-09 | A clerk/staff member can verify PWD/priority ticket details and status | Must | **Yes** | Built (Week 3) |
| MQ-10 ★ | A clerk/staff can manually adjust or override a ticket's priority level upon physically verifying a customer's ID at the counter. | Should | **Yes** | Later |
| MQ-11 ★ | A clerk/staff can export end-of-day queue performance metrics (average wait time, total served, priority ratio, total skipped) to CSV/PDF. | Should | **Yes** | This week |


## Non-functional requirements

A non-functional requirement says **how well** the app must work. Write at least **4**, each with a number or a clear test. Include at least one about data, since that is this week's topic:

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | After the app, server, or database restarts, every waiting ticket keeps its number, status, and position. | Data integrity | Must |
| NFR-02 | Two customers joining the same service at the same moment never get the same ticket number. | Data integrity | Must |
| NFR-03 | A ticket that is served, completed, no-show, or left can never be called again. | Data integrity | Must |
| NFR-04 | Every screen scores 90 or higher in the Lighthouse accessibility check. | Accessibility | Must |
| NFR-05 | No password or secret key is stored in the repository. | Security | Must |
| NFR-06 | The mobile tracker and the clerk’s “call next” action each respond in under 2 seconds. | Performance | Should |


### MVP
- MQ-01, MQ-02, MQ-04, MQ-05, MQ-06, MQ-07, MQ-08, MQ-09, NFR-01, NFR-02, NFR-03, NFR-04, NFR-05
### Out of scope
- **MQ-03 (QR Code Integration)**, since customers can already reach the tracker without it. 


## Feedback

| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
|  A regular customer of MerQry pharmacy | "I have reviewed the details of the queuing system and see a redundancy between MQ-09 and MQ-10. Since you have already starred them, I can easily select the top three requirements: MQ-01, MQ-05, and MQ-09." | I postponed MQ-10, since priority is already set when the ticket is created and verified through MQ-09. I can unified it in MQ-09. |
