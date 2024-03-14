import { html } from "../../html.js";
import { makeRequestBlock } from "../../utils/blocks.js";
import { makeRequestFriend } from "../../utils/friends.js";
import { sendMessage } from "../../utils/chats.js";
import { sendToSocket } from "../../utils/socket.js";

let smiley_array = [
	"😂",
	"😃",
	"😄",
	"😅",
	"🤣",
	"😊",
	"😇",
	"🙂",
	"🙃",
	"😉",
	"😌",
	"😍",
	"🥰",
	"😘",
	"😗",
	"😙",
	"😚",
	"😋",
	"😛",
	"😝",
	"😜",
	"🤪",
	"🤨",
	"🧐",
	"🤓",
	"😎",
	"🤩",
	"🥳",
	"😏",
];

export default (props) => {
	// set displayProfileMenu to "d-none" to hide the menu
	const {username} = props;
	return {
		template: html`<div style="height: 80px; padding-top: 10px">
			<form id="msg_form">
				<div id="type-bar">
					<i class="fa fa-exclamation-circle ml-3 pointer"></i
					><input
						type="text"
						id="msg_input"
						class="ml-3"
						placeholder="Entrez un message pour ${username}" />
					<div style="width: 150px"></div>
					<p
						id="smiley_selector"
						class="emoji-icon-bar d-none d-md-block"
						style="right: 35px"
						>
						😂
					</p>
					<p
						class="emoji-icon-bar d-md-none d-block"
						style="right: 40px"
						id="btn-send-message"
						title="Envoyer le message">
						<i class="fa fa-send"></i>
					</p>
					<p
						id="ask_fight"
						class="emoji-icon-bar"
						style="right: 70px"
						title="Demander un combat"
						>
						⚔️
					</p>
				</div>
			</form>
		</div>`,
		handlers: [
			{
				selector: "#msg_form",
				event: "submit",
				method: function (event) {
					event.preventDefault();
					sendMessage(document.getElementById("msg_input").value, username);
				},
			},
			{
				selector: '#ask_fight',
				event: 'click',
				method: function(event) {
					sendToSocket({action: 'invite', username: username}, 'game');
				}
			},
			{
				selector: "#btn-send-message",
				event: "click",
				method: function (event) {
					sendMessage(document.getElementById("msg_input").value, username);
				},
			},
			{
				selector: "#smiley_selector",
				event: "mouseover",
				method: function (event) {
					event.target.textContent =
						smiley_array[
							Math.floor(Math.random() * smiley_array.length)
						];
				},
			},
			{
				selector: "#smiley_selector",
				event: "click",
				method: function (event) {
					document.getElementById("msg_input").value =
						document.getElementById("msg_input").value +
						event.target.textContent;
				},
			},
		],
	};
};
