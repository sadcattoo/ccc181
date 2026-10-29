## Pet, the PWD customer

> "Daghan kaayog tawo sa mercury ganina nya nahutdan og number..." (interview)

| | |
| --- | --- |
| **Photo or sketch** | ![Persona Photo](screenshots/persona_img.jpg) |
| **Age, role and background** | 23, MSU-IIT graduate, commutes, a PWD and has a heart problem |
| **Goals** | Access Priority Queuing Swiftly, Experience a Clear and Transparent Queue Process, Complete Medicine Purchase Efficiently |
| **Frustrations** | Exhausting Wait Times Without Priority Options, Unclear Queue Status and Overcrowding, Having to Justify Priority Status |
| **Devices and context** | In-Pharmacy Interactive Ticket Kiosk, a touch-screen kiosk located near the entrance where they see or print their ticket, and choose their priority status (Senior, Pregnant, and PWD option). She always stand waiting for her number to be called along with other non-pwd customer. |
| **Tech comfort** | High. As an MSU-IIT graduate in her early 20s, Pet is highly fluent with web dashboards. She can quickly navigate modern user interfaces and strongly prefer fast, self-service digital workflows over manual, paper-based queues. |
| **Accessibility needs** | High Contrast & Large Text Displays and Low Internet Connection Resilience |

### Scenario

Pet enters the crowded pharmacy, feeling chest fatigue after their commute, and heads straight to the entrance kiosk to get his queueing number and choosing "Priority / PWD". The kiosk immediately prints a ticket with a bold priority number and a QR code. To avoid standing and straining their heart, Pet sits on a nearby bench and look at the screen above, a web page that tracks their position in line until their turn is called.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Select PWD priority category to get a ticket | Kiosk Home / Ticket Print | MQ-01 |
| Scan QR code on paper ticket to launch queue tracker | Ticket / Mobile Web Tracker | MQ-02 |
| Receive audio chime and high-contrast screen call out | Overhead Display / Kiosk | MQ-03 |

### What this means for my interface

1. Because Pet suffers from heart fatigue, the kiosk home screen must have a prominent, one-tap "PWD / Priority" button for instant ticketing.
2. Because the pharmacy is crowded and noisy, the overhead display system must combine bold typography with loud audio chimes to announce called turns clearly.
3. Because Pet needs to rest on a bench without relying on strong mobile data, the printed ticket must show large-print queue numbers that sync with clear overhead displays readable from a distance.




## DocG, the pharmacy clerk

> "Wala na ko kabalo kinsa akong unahon kay daghan kaayo sila especially gabii..." (observation)

| | |
| --- | --- |
| **Photo or sketch** | ![Persona Photo 2](screenshots/persona_img2.jpg) |
| **Age, role and background** | 28, full-time pharmacy clerk/dispenser, stands for long shifts, manages high daily customer volume |
| **Goals** | Serve priority and regular patients quickly, manage queue flow smoothly, avoid bottlenecks at dispensing counters |
| **Frustrations** | Loud crowding at counter, manual verification slowing down priority calls, arguments over who arrived first |
| **Devices and context** | Desktop PC or tablet at the pharmacy counter; multi-tasking between queue dashboard, inventory system, and handling medications |
| **Tech comfort** | High — Uses POS systems and inventory software daily; quick with hotkeys and touch interfaces |
| **Accessibility needs** | Large tap targets for fast action, clear status indicators visible at a glance, high-contrast dark/light UI to reduce eye strain during long shifts |

### Scenario

DocG arrives at the busy pharmacy counter, logs into the queue dashboard on the counter PC, and sees a long line of waiting customers. DocG opens the admin interface to view the next incoming ticket, clicks "Call Next" to call priority PWD patient Pet, and instantly updates the status to "Serving" so the overhead screen alerts the customer to come forward.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Call the next priority/regular customer | Queue Dashboard | MQA-01 |
| Verify PWD/Priority ticket details and status | Customer Details | MQA-02 |
| Mark queue number as Serving, Completed, or Skipped | Call Control | MQA-03 |

### What this means for my interface

1. Because DocG works in a fast-paced environment, the admin panel must have a prominent, one-click "Call Next Priority" button.
2. Because DocG multi-tasks between inventory and queueing, the interface must display clear color-coded indicators for PWD vs. regular queues.
3. Because serving times vary, the dashboard must provide quick options to mark tickets as "Serving", "Completed", or "Skipped" in a single tap.