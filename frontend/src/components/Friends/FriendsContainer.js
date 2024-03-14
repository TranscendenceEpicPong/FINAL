import { html } from "../../html.js";
import { getData } from "../../store.js";

export default (props) => {
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div
                        id="friends_container"
                        class="d-cord-container"
                        style="overflow-y: auto">
                        <div class="list-group" style="margin: 25px; border-radius: 15px">
                            <div
                                class="d-flex justify-content-between align-items-center list-group-item">
                                <div class="d-flex align-items-center">
                                    <strong class="d-block">Waiting</strong>
                                </div>
								<form-add-friend></form-add-friend>
                            </div>
							${((getData("friends.waiting") || []).map(friend => {
								return html`
									<friend-waiting-item
										sender_name="${friend.sender.username}"
										sender_avatar="${friend.sender.avatar}"
										receiver_name="${friend.receiver.username}"
										receiver_avatar="${friend.receiver.avatar}"
									/>`;
								})
							)}
                        </div>
                        <div class="list-group" style="margin: 25px; border-radius: 15px">
                            <div
                                class="d-flex justify-content-between align-items-center list-group-item">
                                <div class="d-flex align-items-center">
                                    <strong class="d-block">My friends</strong>
                                </div>
                            </div>
                            ${
                                ((getData("friends.active") || []).map(friend => {
                                    return html`
                                        <friend-item
											sender_name="${friend.sender.username}"
											sender_avatar="${friend.sender.avatar}"
											receiver_name="${friend.receiver.username}"
											receiver_avatar="${friend.receiver.avatar}"
                                        />`;
                                    })
                                )
                            }
                    	</div>
				</div>
			</div>
		`,
	};
};
