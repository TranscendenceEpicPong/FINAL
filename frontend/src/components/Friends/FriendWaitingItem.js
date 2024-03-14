import {html} from "../../html.js";
import { isCurrentUser } from "../../utils/profile.js";

export default (props) => {
    const {sender_name, sender_avatar, receiver_name, receiver_avatar} = props;
    return {
        template: html`
            <div
            	class="d-flex justify-content-between align-items-center list-group-item">
            	<div class="d-flex align-items-center">
            		<img
            			class="rounded-circle"
            			src="${isCurrentUser(sender_name) ? receiver_avatar : sender_avatar}"
            			alt="Profile picture"
            			style="width: 48px; height: 48px" />
            		<div class="ml-3">
            			<strong class="d-block">${isCurrentUser(sender_name) ? receiver_name : sender_name }</strong
            			><small class="text-muted"
            				>${isCurrentUser(sender_name) ? receiver_name : sender_name}</small
            			>
            		</div>
            	</div>
            	<div class="d-flex">
					<add-friend-button username="${isCurrentUser(sender_name) ? receiver_name  : sender_name }" class="${isCurrentUser(sender_name) ? 'd-none' : ''}"></add-friend-button>
					<remove-friend-button username="${isCurrentUser(sender_name) ? receiver_name : sender_name }"></remove-friend-button>
            	</div>
            </div>
        `,
    };
}