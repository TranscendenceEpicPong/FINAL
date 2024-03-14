import { html } from "../../html.js";
import { getData } from "../../store.js";
import { isCurrentUser } from "../../utils/profile.js";

export default (props) => {
	const numFriendsRequest = (getData("friends.waiting") || []).filter((friend) => !isCurrentUser(friend.sender.username)).length;
	return {
		template: html`<div id="nav_container" class="d-md-block d-none">
			<div id="nav_main">
				<div style="overflow: auto; flex: 1">
					<div
						class="d-block d-md-none pointer"
						style="
							color: white;
							font-size: 26px;
							padding-top: 25px;
							padding-right: 25px;
							padding-left: 25px;
						"
						id="menu_close_button">
						<i class="fa fa-close"></i>
					</div>
					<div class="text-center mt-4">
						<img src="/assets/img/42_logo.svg" style="width: 50px" class="mb-4" />
						<menu-link icon="fa fa-heart" href="/friends" pings="${numFriendsRequest}">Friends</menu-link>
						<menu-link icon="fas fa-ban" href="/blocks">Blocks</menu-link>
						<menu-link icon="fa fa-gamepad" href="/games">Game</menu-link>
						<menu-link icon="fa fa-trophy" href="/tournaments">Tournaments</menu-link>
					</div>
					<h6
						class="text-left mt-3 mb-2"
						style="
					margin-bottom: 0px;
					margin-left: 10px;
					font-size: 13px;
					color: #aaaaaa;
				">
						Private messages
					</h6>
					${(getData("friends.active") || []).map((friend) => {
						return html`<pm-item
							href="${isCurrentUser(friend.sender.username) ? friend.receiver.avatar: friend.sender.avatar}"
							name="${isCurrentUser(friend.sender.username) ? friend.receiver.username: friend.sender.username}"
							link="/chats/${isCurrentUser(friend.sender.username) ? friend.receiver.username: friend.sender.username}"
							status="${isCurrentUser(friend.sender.username) ? friend.receiver.status: friend.sender.status}"></pm-item>`
					})}
				</div>
				<short-profile-menu></short-profile-menu>
			</div>
		</div> `,
		handlers: [
			{
				selector: "#menu_close_button",
				event: "click",
				method: () => {
					document.getElementById("nav_container").classList.add("d-none");
				},
			}
		],
	};
};
