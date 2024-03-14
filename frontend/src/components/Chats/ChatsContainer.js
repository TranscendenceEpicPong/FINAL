import { html } from "../../html.js";
import { loadPage } from "../../router.js";
import { getData } from "../../store.js";
import { getMessagesWith } from "../../utils/chats.js";



export default (props) => {
	const {username, avatar} = props;
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div
						id="chat_container"
						class="active_container cord-container">
						<img id="show-profile" style="position: fixed; top: 10px; right: 10px; width: 50px; height: 50px; padding: 0; border-radius: 100%;" class="btn btn-secondary" src="${avatar}"/>
						<div class="d-flex" id="main_container">
							<div
								id="chat_msgs"
								class="mb-3"
								style="
								width: 100%;
								margin-right: 25px;
								margin-left: 25px;
								margin-top: auto !important;
							">
								<div class="text-white mt-3 user-select-none">
									<h6 class="card-title mb-0">
									Le début d'une grande amitié
									</h6>
									<p class="card-text" style="color: #dfdfdf">
										C'est le début de votre conversation avec ${username}
									</p>
								</div>
								<hr style="background: #4b5157" />
								${
									(getMessagesWith(username) || []).map(
										(message) => {
											return html`
												<chats-message
													username="${message.sender.username}"
													avatar="${message.sender.avatar}"
												>
													${message.content}
												</chats-message>
											`;
										}
									)
								}
							</div>
						</div>
						<type-bar username="${username}"></type-bar>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#show-profile",
				event: "click",
				method: function () {
					loadPage(`/profile/${username}`);
				},
			},
		],
	};
};
