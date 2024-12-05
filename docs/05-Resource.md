# Resource

### MN-CSE

<img src="./img/05-resource-MN-CSE.png" alt="Example Image" width="180px" height="350px">

<br/>
<br/>

### IN-CSE

<img src="./img/05-reousrce-IN-CSE.png" alt="Example Image" width="180px" height="470px">

**The input time format is `HH:MM`**.

<br/>

# Control Noise Cancellation Time

<img src="./img/05-resource-IN-AE-to-ADN-AE.png" alt="Example Image" width="800px" height="350px">

1. The user requests noise cancellation for a specific time period.
2. The cloud service saves the user-defined time period as a resource.
3. When the requested time arrives, the system updates `ExecutionState` to `On`.
4. When `ExecutionState` is updated to `On`, the gateway's `DeviceStatus` is set to `start`.
5. When the `DeviceStatus` changes to 'start,' the speaker`AE` begins noise cancellation processing.

If it is outside the user-requested time period, `ExecutionState` is set to `Off`, and `DeviceStatus` is set to `stop`, halting noise cancellation.

<br/>

# Noise Data Collection

<img src="./img/05-resource-ADN-AE-to-IN-AE.png" alt="Example Image" width="600px" height="200px">

1. The sensor `AE` updates the average noise value collected every hour.
2. Using the CSR, the `IN-CSE` retrieves the average noise data from the `MN-CSE`.
3. The `IN-CSE` stores the retrieved data. This data can be used to provide users with hourly noise levels or to recommend noise cancellation times.
