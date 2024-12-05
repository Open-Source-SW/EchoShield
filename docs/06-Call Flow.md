# Call Flow

### Registration

![initial](./img/06-registration.png)
**Registration**: Register the Noise Detection Application, Speaker Application, Gateway Application, and Smartphone Application.

<br/>
<br/>

### Data Management & Repository

![initial](./img/06-initial-resource.png)
**Initial resource creation**:
container resource, contentInstance resource of a specific container resource, subscription resource of a specific container resource, group resource management.

<br/>

### Access Control Policy

![access-control-policy](./img/06-access-control-policy.png)
**Access Control Policy**:
Access control policy creation granting AND-AE and IN-AE can access to noise detection device container and noise-canceling speaker containe.

<br/>
<br/>

### Data Management & Repository

![group-resource-creation](./img/06-group-resource-creation.png)
**Group resource creation**:
Group resource creation, discovery group resources and update group resource members.

<br/>
<br/>

### Subscription

![subscription](./img/06-subscription.png)
**Subscription**: Subscription setup to receive notifications about value changes from IN-AE.

<br/>
<br/>

### Discovery and Retrieval

![discovery&retrieval](./img/06-discovery&retrieval-0.png)
**Discovery and retrieve of contentInstance resource**: Discover container resource and retrieve the contentInstance resource of a specific container resource
The purpose is to ensure the latest state is updated for the user to view and control devices efficiently.

<br/>

![discovery&retrieval](./img/06-discovery&retrieval-1.png)
**Discovery and retrieve of group resource**:
Discover the group resource and retrieve the contentInstance resource of group resources
The purpose is to ensure the latest state is updated for the user to view and control devices efficiently.

<br/>
<br/>

### Resource update(Notification)

![single-update](./img/06-single-resource-update.png)
**Single speaker remote control**: Single speakers that are discovered are able to be switched on and off via a smartphone application and send notifications.

<br/>

![multiple-update](./img/06-single-resource-update.png)
**Multiple speaker remote control**: Multiple speakers that are discovered are able to be switched on and off via a smartphone application and send notifications.
