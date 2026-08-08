# Software-Defined Vehicles (SDV)

## Bilingual Technical Summary / Tóm tắt kỹ thuật song ngữ

**Based on / Dựa trên:** *The Rise of the Software-Defined Vehicle:
Architectures, Enabling Technologies, and Future Opportunities*\
**Authors / Tác giả:** Eirini Liotou, Dimitra Tzelalidou, Gerasimos
Christodoulou\
**arXiv:** 2605.30001v1 (28 May 2026)\
**Source:** https://arxiv.org/html/2605.30001v1

> **Purpose / Mục đích:** This document is a concise bilingual study
> guide, not a verbatim translation of the paper.\
> Tài liệu này là bản tổng hợp song ngữ dễ học, không phải bản dịch
> nguyên văn của bài báo.

------------------------------------------------------------------------

## 1. Executive Summary / Tóm tắt tổng quan

### English

A **Software-Defined Vehicle (SDV)** is a vehicle whose capabilities,
behavior, user experience, and increasingly its lifecycle are primarily
controlled and extended through software rather than being permanently
fixed by hardware.

The automotive industry is moving from vehicles containing many
distributed Electronic Control Units (ECUs) toward **domain, zonal, and
centralized architectures** built around high-performance computing.
This transition enables software/hardware decoupling, service-oriented
software, Over-the-Air (OTA) updates, AI-assisted and automated driving,
cloud/edge integration, and Vehicle-to-Everything (V2X) connectivity.

An SDV can therefore be understood as a **distributed computing platform
on wheels**: sensors observe the physical world, zonal controllers
aggregate local inputs and outputs, centralized computers execute
critical software and AI workloads, networking connects components and
external infrastructure, and cloud/edge platforms support fleet
services, analytics, updates, and learning.

The major challenges are cybersecurity, functional safety, software
complexity, interoperability, standardization, data volume, real-time
constraints, and energy consumption. Future directions include Digital
Twins, Federated Learning, proactive cybersecurity, and potentially
**AI-Defined Vehicles**.

### Tiếng Việt

**Software-Defined Vehicle (SDV -- Xe được định nghĩa bằng phần mềm)**
là chiếc xe mà khả năng, hành vi, trải nghiệm người dùng và ngày càng
nhiều phần trong vòng đời sản phẩm được điều khiển và mở rộng chủ yếu
bằng phần mềm, thay vì bị cố định bởi phần cứng.

Ngành ô tô đang chuyển từ kiến trúc gồm rất nhiều **ECU phân tán** sang
**Domain Architecture, Zonal Architecture và Centralized Architecture**,
sử dụng các máy tính hiệu năng cao. Sự chuyển đổi này cho phép tách
software khỏi hardware, xây dựng phần mềm theo service, cập nhật OTA,
tích hợp AI/lái xe tự động, kết nối cloud/edge và V2X.

Vì vậy, có thể hiểu SDV như một **nền tảng điện toán phân tán có bánh
xe**: sensor quan sát thế giới vật lý; zone controller tập hợp tín hiệu
cục bộ; máy tính trung tâm chạy software và AI; mạng kết nối các thành
phần; cloud/edge hỗ trợ quản lý đội xe, phân tích dữ liệu, cập nhật và
học máy.

Những thách thức lớn gồm cybersecurity, functional safety, độ phức tạp
software, interoperability, standardization, dữ liệu khổng lồ, yêu cầu
real-time và mức tiêu thụ năng lượng. Các hướng tương lai nổi bật gồm
Digital Twin, Federated Learning, proactive cybersecurity và xa hơn là
**AI-Defined Vehicle**.

------------------------------------------------------------------------

## 2. The Core Transformation / Sự chuyển đổi cốt lõi

``` text
Traditional Vehicle / Xe truyền thống
Hardware-defined
      │
      ▼
Many distributed ECUs
Nhiều ECU phân tán
      │
      ▼
Domain Architecture
Kiến trúc theo miền chức năng
      │
      ▼
Zonal Architecture
Kiến trúc theo vùng vật lý
      │
      ▼
Centralized High-Performance Computing
Điện toán hiệu năng cao tập trung
      │
      ▼
Software-Defined Vehicle
Xe được định nghĩa bằng phần mềm
      │
      ▼
Potential future / Tương lai tiềm năng
AI-Defined Vehicle
```

### Key idea / Ý chính

**EN:** In a traditional vehicle, adding or changing a feature often
requires changes to tightly coupled hardware and software. In an SDV,
standardized interfaces and software abstraction increasingly allow
functions to evolve independently of specific hardware.

**VI:** Trong xe truyền thống, việc thêm hoặc thay đổi tính năng thường
liên quan chặt tới cả hardware và software. Với SDV, các interface chuẩn
hóa và lớp trừu tượng software giúp chức năng có thể phát triển độc lập
hơn với phần cứng cụ thể.

------------------------------------------------------------------------

## 3. Evolution of Vehicle E/E Architecture / Tiến hóa kiến trúc điện-điện tử

### 3.1 Distributed ECU Architecture / Kiến trúc ECU phân tán

``` text
[ECU Engine]   [ECU Door]   [ECU Seat]
      \            |            /
       \           |           /
        ------ Vehicle Bus ------
       /           |           \
[ECU Brake]   [ECU Camera]   [ECU IVI]
```

**EN:** Individual functions are commonly tied to dedicated ECUs. This
creates many controllers, extensive wiring, complex dependencies, and
difficult integration.

**VI:** Mỗi chức năng thường gắn với một ECU riêng. Điều này dẫn tới
nhiều controller, hệ thống dây phức tạp, dependency lớn và khó tích hợp.

### 3.2 Domain Architecture / Kiến trúc theo domain

``` text
             Vehicle Backbone
          ┌──────┬──────┬──────┐
          │      │      │      │
       ADAS   Body   Powertrain  IVI
       Domain Domain   Domain   Domain
```

**EN:** Related functions are consolidated into domain controllers,
reducing fragmentation while still organizing the vehicle primarily by
function.

**VI:** Các chức năng liên quan được gom vào domain controller, giảm
phân mảnh nhưng xe vẫn chủ yếu được tổ chức theo nhóm chức năng.

### 3.3 Zonal Architecture / Kiến trúc zonal

``` text
                   ┌──────────────────┐
                   │ Central Computer │
                   │  / HPC Platform  │
                   └────────┬─────────┘
                            │
                  High-Speed Ethernet
             ┌──────────────┼──────────────┐
             │              │              │
        ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
        │ Zone FL │    │ Zone FR │    │ Zone Rear│
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
       Sensors /       Sensors /       Sensors /
       Actuators       Actuators       Actuators
```

**EN:** Controllers are organized by physical location. A zone
controller connects nearby sensors and actuators to a high-speed
backbone and central computing resources.

**VI:** Controller được tổ chức theo vị trí vật lý trên xe. Zone
controller kết nối sensor/actuator ở gần nó với backbone tốc độ cao và
hệ thống tính toán trung tâm.

**Benefits / Lợi ích:** - Less wiring / Giảm dây điện - Lower weight /
Giảm trọng lượng - Easier scalability / Dễ mở rộng - Better software
abstraction / Tách software-hardware tốt hơn - Better support for
centralized computing / Hỗ trợ điện toán tập trung

------------------------------------------------------------------------

## 4. SDV Software Stack / Ngăn xếp phần mềm SDV

``` text
┌─────────────────────────────────────┐
│ Applications / Ứng dụng             │
│ ADAS • Navigation • IVI • AI        │
├─────────────────────────────────────┤
│ Services / SOA                      │
│ Vehicle APIs • Reusable Services    │
├─────────────────────────────────────┤
│ Middleware                          │
│ Communication • Discovery • IPC     │
├─────────────────────────────────────┤
│ OS / RTOS                           │
│ Scheduling • Memory • Isolation     │
├─────────────────────────────────────┤
│ Hardware / HPC / ECUs               │
└─────────────────────────────────────┘
```

### OS and RTOS

**EN:** Automotive systems need operating systems that manage hardware
resources, processes, memory, and communication. Safety-critical
functions often require an **RTOS** because execution must meet
deterministic timing constraints.

**VI:** Hệ thống automotive cần OS để quản lý tài nguyên phần cứng,
process, memory và communication. Các chức năng safety-critical thường
cần **RTOS** vì tác vụ phải đáp ứng deadline xác định.

### Middleware

**EN:** Middleware hides hardware and operating-system differences and
provides common communication mechanisms between software components.

**VI:** Middleware che giấu khác biệt giữa hardware/OS và cung cấp cơ
chế giao tiếp chung giữa các software component.

### Service-Oriented Architecture (SOA)

``` text
                   Applications
                /       |       \
               v        v        v
        ┌──────────┐ ┌────────┐ ┌───────────┐
        │Navigation│ │  ADAS  │ │ Mobile UI │
        └────┬─────┘ └───┬────┘ └─────┬─────┘
             │           │            │
             └───────────┼────────────┘
                         v
                ┌────────────────┐
                │ Service Layer  │
                ├────────────────┤
                │ Speed Service  │
                │ GPS Service    │
                │ Battery Service│
                │ Camera Service │
                │ Climate Service│
                └────────────────┘
```

**EN:** Functions are exposed as reusable services instead of being
embedded inside monolithic applications. This improves modularity,
reuse, maintainability, and hardware independence.

**VI:** Chức năng được cung cấp dưới dạng service tái sử dụng thay vì
nằm cứng trong một ứng dụng monolithic. Điều này tăng modularity, reuse,
maintainability và giảm phụ thuộc hardware.

------------------------------------------------------------------------

## 5. OTA Updates / Cập nhật qua mạng

``` text
Cloud / OEM Backend
        │
        │ Signed Update
        ▼
 Connectivity: 4G / 5G / Wi-Fi
        │
        ▼
┌───────────────────────┐
│ Vehicle Update Manager│
└──────────┬────────────┘
           │
     Verify / Validate
           │
           ▼
       Installation
           │
      ┌────┴────┐
      │         │
   Success    Failure
      │         │
   Activate   Rollback
```

**EN:** OTA enables vehicles to receive bug fixes, security patches,
performance improvements, and new capabilities after production. A
robust OTA process requires authentication, integrity checking,
compatibility validation, safe activation, and rollback.

**VI:** OTA cho phép xe nhận bug fix, security patch, cải thiện hiệu
năng và tính năng mới sau khi xuất xưởng. Quy trình OTA an toàn cần
authentication, kiểm tra integrity, compatibility, activation an toàn và
rollback khi lỗi.

------------------------------------------------------------------------

## 6. Automated Driving Pipeline / Pipeline lái xe tự động

``` text
Physical World / Môi trường thực
                │
                ▼
 ┌─────────────────────────────┐
 │ Camera • Radar • LiDAR      │
 │ Ultrasonic • GNSS • IMU     │
 └──────────────┬──────────────┘
                ▼
        Perception / Detection
                │
                ▼
       Sensor Fusion / Tracking
                │
                ▼
          Localization + Map
                │
                ▼
       Prediction / Planning
                │
                ▼
          Motion Planning
                │
                ▼
           Vehicle Control
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
     Steering  Brake   Throttle
```

### Perception / Nhận thức môi trường

**EN:** Cameras provide rich visual information; radar is robust in
adverse conditions and measures range/velocity; LiDAR provides detailed
3D geometry. Sensor fusion combines their complementary strengths.

**VI:** Camera cung cấp thông tin hình ảnh phong phú; radar hoạt động
tốt trong điều kiện xấu và đo khoảng cách/vận tốc; LiDAR cung cấp hình
học 3D chi tiết. Sensor fusion kết hợp ưu điểm của nhiều sensor.

### Localization / Định vị

Typical sources / Nguồn dữ liệu phổ biến:

``` text
GNSS/GPS + IMU + RTK + Dead Reckoning + Map
                       │
                       ▼
             Vehicle Position / Pose
```

### SLAM

**SLAM = Simultaneous Localization and Mapping**

**EN:** The system estimates its own position while simultaneously
building or updating a representation of the environment.

**VI:** Hệ thống vừa xác định vị trí của chính nó, vừa xây dựng hoặc cập
nhật bản đồ môi trường.

------------------------------------------------------------------------

## 7. AI in SDVs / AI trong SDV

``` text
Sensor Data
    │
    ▼
AI Perception
Object / Lane / Scene Detection
    │
    ▼
Prediction
What will other actors do?
    │
    ▼
Decision / Planning
What should the vehicle do?
    │
    ▼
Control
Steer • Brake • Accelerate
```

AI technologies discussed in the SDV ecosystem include:

-   **CNN (Convolutional Neural Network):** visual perception.
-   **RNN (Recurrent Neural Network):** temporal/sequential information.
-   **Reinforcement Learning (RL):** adaptive decision-making and
    control.
-   **LLM-based interfaces:** an emerging direction for human-machine
    interaction and intelligent vehicle services.

**VI:** AI không chỉ là trợ lý hội thoại. Nó có thể tham gia perception,
prediction, planning, decision-making, personalization và security. Tuy
nhiên, AI cũng làm tăng compute demand, power consumption và yêu cầu
validation.

------------------------------------------------------------------------

## 8. Vehicle + Edge + Cloud / Xe + Edge + Cloud

``` text
                         ┌──────────────────┐
                         │      CLOUD       │
                         │ Fleet Management │
                         │ Big Data / AI    │
                         │ OTA / Services   │
                         └────────┬─────────┘
                                  │
                              Internet
                                  │
                         ┌────────▼─────────┐
                         │    EDGE / FOG    │
                         │ Low-latency Apps │
                         └────────┬─────────┘
                                  │
                          5G / V2X / SDN
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
          Vehicle A  ←── V2V ─→ Vehicle B ←── V2V ─→ Vehicle C
             │                    │                    │
             └──────────── Road Infrastructure ────────┘
                               V2I / V2X
```

**EN:** SDVs increasingly operate as nodes in a larger **Internet of
Vehicles (IoV)**. Edge computing reduces latency and network load, while
cloud platforms provide large-scale analytics, fleet management,
storage, training, and software distribution.

**VI:** SDV ngày càng trở thành một node của **Internet of Vehicles
(IoV)**. Edge computing giảm latency và tải mạng; cloud cung cấp
analytics quy mô lớn, fleet management, storage, model training và phân
phối software.

------------------------------------------------------------------------

## 9. Main Challenges / Những thách thức chính

  -----------------------------------------------------------------------
  Challenge               English                 Tiếng Việt
  ----------------------- ----------------------- -----------------------
  Big Data                Sensors generate very   Sensor tạo lượng dữ
                          large data volumes; not liệu rất lớn; không thể
                          everything can be       liên tục gửi tất cả lên
                          continuously uploaded   cloud.
                          to the cloud.           

  Cybersecurity           Connectivity, OTA, V2X, Connectivity, OTA, V2X,
                          infotainment and APIs   infotainment và API làm
                          expand the attack       tăng attack surface.
                          surface.                

  Functional Safety       Failures can have       Lỗi hệ thống có thể gây
                          direct physical         hậu quả trực tiếp tới
                          consequences.           an toàn vật lý.

  Energy Efficiency       HPC and AI workloads    HPC và AI tiêu thụ điện
                          consume power and       và sinh nhiệt.
                          generate heat.          

  Interoperability        Different OEM stacks    Các stack khác nhau
                          must communicate        giữa OEM cần interface
                          through compatible      và standard tương
                          interfaces and          thích.
                          standards.              

  Complexity              More software and       Software và dependency
                          dependencies make       tăng làm validation và
                          validation and          quản lý vòng đời khó
                          lifecycle management    hơn.
                          harder.                 

  Real-Time Behavior      Critical functions must Chức năng quan trọng
                          respond within bounded  phải phản hồi trong
                          deadlines.              deadline xác định.
  -----------------------------------------------------------------------

### Security relationship / Quan hệ giữa security và safety

``` text
More Connectivity
      │
      ▼
Larger Attack Surface
      │
      ▼
Cybersecurity Incident
      │
      ▼
Possible Control/System Failure
      │
      ▼
Physical Safety Risk
```

In automotive systems, **cybersecurity can become a functional/physical
safety issue**.

Trong automotive, **cybersecurity có thể trực tiếp trở thành vấn đề
functional/physical safety**.

------------------------------------------------------------------------

## 10. Future Directions / Hướng phát triển tương lai

### 10.1 Digital Twin

``` text
┌──────────────────┐       telemetry       ┌──────────────────┐
│ Physical Vehicle │ ────────────────────> │  Digital Twin    │
└──────────────────┘                       └────────┬─────────┘
                                                  │
                                  Simulation / Validation
                                                  │
                                       ┌──────────▼─────────┐
                                       │ OTA / Maintenance  │
                                       │ Decision Support   │
                                       └────────────────────┘
```

**EN:** A digital representation of a vehicle can support simulation,
diagnostics, predictive maintenance, and potentially safer validation
before deploying changes.

**VI:** Bản sao số của xe có thể hỗ trợ simulation, diagnostics,
predictive maintenance và validation trước khi triển khai thay đổi lên
xe thật.

### 10.2 Federated Learning

``` text
 Vehicle A          Vehicle B          Vehicle C
    │                   │                  │
Local Training      Local Training     Local Training
    │                   │                  │
    └──────── Model Updates Only ──────────┘
                        │
                        ▼
                Federated Aggregator
                        │
                        ▼
                  Improved Model
```

**EN:** Vehicles can train models locally and share model updates rather
than centralizing all raw sensor data.

**VI:** Xe có thể train model cục bộ và chia sẻ model update thay vì tập
trung toàn bộ raw sensor data.

### 10.3 Proactive Cybersecurity

**EN:** Security is expected to increasingly use anomaly and intrusion
detection at the vehicle or edge level to identify threats before they
cause serious impact.

**VI:** Security có xu hướng chuyển sang phát hiện anomaly/intrusion
ngay trên xe hoặc edge nhằm phát hiện sớm mối đe dọa.

### 10.4 Toward AI-Defined Vehicles

``` text
Hardware-Defined
      │
      ▼
Software-Defined
      │
      ▼
AI-Enhanced SDV
      │
      ▼
AI-Defined Vehicle ?
```

**EN:** A possible next stage is a vehicle where AI becomes deeply
involved not only in applications but also in system adaptation,
interaction, decision-making, security, and optimization.

**VI:** Bước tiếp theo có thể là chiếc xe nơi AI không chỉ nằm ở
application mà tham gia sâu vào adaptation, interaction,
decision-making, security và optimization.

------------------------------------------------------------------------

## 11. One-Page Mental Model / Mô hình ghi nhớ một trang

``` text
                            CLOUD
                 AI • Fleet • OTA • Data
                              │
                        EDGE / NETWORK
                    5G • V2X • SDN • Fog
                              │
══════════════════════════════╪══════════════════════════════
                 SOFTWARE-DEFINED VEHICLE
══════════════════════════════╪══════════════════════════════
                              │
              ┌─────────────────────────────┐
              │ Applications                │
              │ ADAS • IVI • Navigation • AI│
              ├─────────────────────────────┤
              │ Services / SOA              │
              ├─────────────────────────────┤
              │ Middleware                  │
              ├─────────────────────────────┤
              │ OS / RTOS                   │
              ├─────────────────────────────┤
              │ Central HPC                 │
              └──────────────┬──────────────┘
                             │
                    Ethernet Backbone
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
              Zone A      Zone B      Zone C
                 │           │           │
             Sensors / Actuators / Local ECUs
                 │
                 ▼
             PHYSICAL WORLD
```

**Mental model / Cách nhớ:**\
**Sensors → Zones → Central Compute → OS/Middleware → Services → Apps/AI
→ Network → Edge/Cloud**

------------------------------------------------------------------------

# 12. Technical Glossary / Thuật ngữ kỹ thuật

  ---------------------------------------------------------------------------
  Term                    Full name / Meaning         Giải thích tiếng Việt
  ----------------------- --------------------------- -----------------------
  **SDV**                 Software-Defined Vehicle    Xe có chức năng và khả
                                                      năng được định
                                                      nghĩa/phát triển chủ
                                                      yếu bằng software.

  **ECU**                 Electronic Control Unit     Bộ điều khiển điện tử
                                                      thực hiện một hoặc
                                                      nhiều chức năng trong
                                                      xe.

  **E/E Architecture**    Electrical/Electronic       Kiến trúc điện và điện
                          Architecture                tử tổng thể của xe.

  **Domain Architecture** Functional-domain           Gom controller theo
                          architecture                nhóm chức năng như
                                                      ADAS, body, powertrain,
                                                      infotainment.

  **Zonal Architecture**  Location-based E/E          Gom kết nối/controller
                          architecture                theo vùng vật lý của
                                                      xe.

  **Zone Controller**     Local zonal controller      Controller quản lý
                                                      sensor/actuator và kết
                                                      nối trong một vùng vật
                                                      lý.

  **HPC / HPCU**          High-Performance Computer / Máy tính hiệu năng cao
                          Computing Unit              chạy nhiều workload tập
                                                      trung trên xe.

  **SOA**                 Service-Oriented            Kiến trúc phần mềm chia
                          Architecture                chức năng thành các
                                                      service có interface rõ
                                                      ràng.

  **Middleware**          Software                    Lớp trung gian giúp
                          integration/communication   component giao tiếp và
                          layer                       giảm phụ thuộc
                                                      hardware/OS.

  **OS**                  Operating System            Hệ điều hành quản lý
                                                      tài nguyên và software
                                                      execution.

  **RTOS**                Real-Time Operating System  Hệ điều hành thời gian
                                                      thực, đảm bảo tác vụ
                                                      đáp ứng timing
                                                      constraint.

  **AUTOSAR**             AUTomotive Open System      Chuẩn/kiến trúc phần
                          ARchitecture                mềm automotive nhằm
                                                      tăng tính chuẩn hóa và
                                                      portability.

  **SOME/IP**             Scalable service-Oriented   Giao thức/middleware
                          MiddlewarE over IP          communication theo
                                                      hướng service trong
                                                      automotive Ethernet/IP.

  **OTA**                 Over-the-Air                Cập nhật
                                                      software/firmware từ xa
                                                      qua mạng.

  **Rollback**            Revert to previous version  Quay lại phiên bản ổn
                                                      định trước nếu update
                                                      thất bại.

  **ADAS**                Advanced Driver Assistance  Hệ thống hỗ trợ người
                          Systems                     lái nâng cao.

  **IVI**                 In-Vehicle Infotainment     Hệ thống thông tin và
                                                      giải trí trong xe.

  **Sensor Fusion**       Combining multiple sensor   Kết hợp
                          sources                     camera/radar/LiDAR...
                                                      để tạo nhận thức môi
                                                      trường đáng tin cậy
                                                      hơn.

  **LiDAR**               Light Detection and Ranging Sensor sử dụng ánh
                                                      sáng/laser để đo khoảng
                                                      cách và tạo biểu diễn
                                                      3D.

  **Radar**               Radio Detection and Ranging Sensor dùng sóng vô
                                                      tuyến để đo khoảng
                                                      cách/vận tốc đối tượng.

  **GNSS**                Global Navigation Satellite Hệ thống định vị vệ
                          System                      tinh; GPS là một hệ
                                                      thống GNSS.

  **IMU**                 Inertial Measurement Unit   Cảm biến quán tính đo
                                                      gia tốc và chuyển động
                                                      quay.

  **RTK**                 Real-Time Kinematic         Kỹ thuật hiệu chỉnh
                                                      GNSS để đạt độ chính
                                                      xác vị trí cao hơn.

  **Dead Reckoning**      Position estimation from    Ước lượng vị trí mới từ
                          motion                      vị trí trước đó và dữ
                                                      liệu chuyển động.

  **SLAM**                Simultaneous Localization   Đồng thời định vị và
                          and Mapping                 xây dựng/cập nhật bản
                                                      đồ môi trường.

  **Perception**          Environment understanding   Quá trình nhận biết
                                                      lane, object,
                                                      pedestrian, vehicle và
                                                      môi trường.

  **Localization**        Vehicle pose estimation     Xác định vị trí và
                                                      hướng của xe.

  **Motion Planning**     Trajectory/path planning    Tính đường đi/quỹ đạo
                                                      phù hợp với mục tiêu và
                                                      môi trường.

  **CNN**                 Convolutional Neural        Neural network thường
                          Network                     dùng cho computer
                                                      vision.

  **RNN**                 Recurrent Neural Network    Neural network xử lý dữ
                                                      liệu chuỗi/thời gian.

  **RL**                  Reinforcement Learning      Học tăng cường thông
                                                      qua reward và
                                                      interaction với môi
                                                      trường.

  **LLM**                 Large Language Model        Mô hình ngôn ngữ lớn,
                                                      có thể hỗ trợ giao diện
                                                      người-xe và intelligent
                                                      services.

  **V2V**                 Vehicle-to-Vehicle          Giao tiếp giữa xe với
                                                      xe.

  **V2I**                 Vehicle-to-Infrastructure   Giao tiếp giữa xe và hạ
                                                      tầng giao thông.

  **V2X**                 Vehicle-to-Everything       Khái niệm tổng quát cho
                                                      giao tiếp xe với xe, hạ
                                                      tầng và các thực thể
                                                      khác.

  **IoV**                 Internet of Vehicles        Hệ sinh thái mạng kết
                                                      nối xe, hạ tầng, edge
                                                      và cloud.

  **SDIoV**               Software-Defined Internet   IoV sử dụng các nguyên
                          of Vehicles                 lý software-defined để
                                                      quản lý linh hoạt hơn.

  **SDN**                 Software-Defined Networking Tách control plane khỏi
                                                      data plane để quản lý
                                                      mạng bằng software.

  **Edge Computing**      Compute near the data       Xử lý dữ liệu gần xe để
                          source                      giảm latency và
                                                      bandwidth.

  **Fog Computing**       Distributed compute between Lớp tính toán phân tán
                          edge and cloud              nằm giữa thiết bị edge
                                                      và cloud.

  **Digital Twin**        Digital representation of a Bản sao/mô hình số của
                          physical system             xe phục vụ simulation,
                                                      monitoring và
                                                      prediction.

  **Federated Learning**  Distributed                 Train model cục bộ trên
                          privacy-oriented ML         nhiều node và tổng hợp
                          training                    model update thay vì
                                                      raw data.

  **Functional Safety**   Safety against              Đảm bảo lỗi hệ thống
                          malfunctioning behavior     không tạo ra rủi ro
                                                      không chấp nhận được.

  **Cybersecurity**       Protection against digital  Bảo vệ xe, network,
                          attacks                     software và data trước
                                                      tấn công mạng.

  **Attack Surface**      Exposed points attackers    Tập hợp
                          may target                  interface/component có
                                                      khả năng bị khai thác.

  **Interoperability**    Ability of systems to work  Khả năng các hệ
                          together                    thống/vendor khác nhau
                                                      tương tác đúng với
                                                      nhau.

  **Deterministic**       Predictable bounded         Hành vi/thời gian phản
                          behavior/timing             hồi có giới hạn và dự
                                                      đoán được.

  **Real-Time**           Must respond within timing  Hệ thống phải hoàn
                          constraints                 thành tác vụ trong
                                                      deadline quy định.

  **API**                 Application Programming     Interface để software
                          Interface                   component/service giao
                                                      tiếp với nhau.

  **Ethernet Backbone**   High-speed in-vehicle       Mạng Ethernet tốc độ
                          Ethernet network            cao đóng vai trò
                                                      backbone truyền dữ liệu
                                                      trong xe.
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

## 13. Six Things to Remember / 6 điều quan trọng nhất

1.  **EN:** The vehicle is becoming a software platform.\
    **VI:** Chiếc xe đang trở thành một software platform.

2.  **EN:** Distributed ECUs are moving toward zonal and centralized
    high-performance computing.\
    **VI:** ECU phân tán đang chuyển dần sang zonal architecture và
    centralized HPC.

3.  **EN:** OS + middleware + SOA provide the software foundation.\
    **VI:** OS + middleware + SOA tạo thành nền tảng software.

4.  **EN:** OTA allows the vehicle to evolve after it leaves the
    factory.\
    **VI:** OTA giúp chiếc xe tiếp tục phát triển sau khi xuất xưởng.

5.  **EN:** AI, V2X, edge, and cloud turn the vehicle into part of a
    distributed intelligent system.\
    **VI:** AI, V2X, edge và cloud biến chiếc xe thành một phần của hệ
    thống thông minh phân tán.

6.  **EN:** Safety, security, energy, data, standards, and complexity
    are as important as raw computing power.\
    **VI:** Safety, security, năng lượng, dữ liệu, standard và
    complexity quan trọng không kém sức mạnh tính toán.

------------------------------------------------------------------------

## 14. Final Takeaway / Kết luận dễ nhớ

> **EN:** A Software-Defined Vehicle is the transition from "a
> mechanical product that contains software" to "a connected,
> distributed computing platform whose capabilities continuously evolve
> through software."

> **VI:** Software-Defined Vehicle là sự chuyển đổi từ "một sản phẩm cơ
> khí có chứa phần mềm" thành "một nền tảng điện toán phân tán, có kết
> nối, với khả năng liên tục phát triển thông qua phần mềm."

A possible next transition is:

``` text
Mechanical Vehicle
        ↓
Electronic Vehicle
        ↓
Connected Vehicle
        ↓
Software-Defined Vehicle
        ↓
AI-Defined Vehicle
```

------------------------------------------------------------------------

## Reference / Tài liệu tham khảo

Liotou, E., Tzelalidou, D., & Christodoulou, G. (2026). *The Rise of the
Software-Defined Vehicle: Architectures, Enabling Technologies, and
Future Opportunities*. arXiv:2605.30001v1.

Source: https://arxiv.org/html/2605.30001v1

**Note:** Diagrams in this document are simplified conceptual diagrams
created for explanation and study purposes.
