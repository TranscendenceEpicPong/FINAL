// Import our custom CSS
import "./scss/main.scss";

// Import all of Bootstrap's JS
//import * as bootstrap from "bootstrap";

import { registerComponent } from "./registerComponent.js";
import {initRouter, loadPage} from "./router.js";
import {initStore, resetStore, setData} from "./store.js";
import { initAccess } from "./utils/profile.js";

// Components
import NavLink from "./components/Navigation/NavLink.js";
import MainContainer from "./components/MainContainer.js";
import NavContainer from "./components/Navigation/NavContainer.js";
import MenuLink from "./components/Navigation/MenuLink.js";

// Authentication
import LoginButton from "./components/Auth/Login/LoginButton.js";
import LoginForm from "./components/Auth/Login/LoginForm.js";
import RegisterForm from "./components/Auth/Register/RegisterForm.js";
import LogoutButton from "./components/Auth/Logout/LogoutButton.js";

// 2FA
import A2FFormEnable from "./components/2FA/FormEnable.js";
import A2FFormDisable from "./components/2FA/FormDisable.js";
import A2FForm from "./components/2FA/2FAForm.js";

// Game
import GameLink from "./components/NavLinks/GameLink.js";
import StartGame from "./components/Game/StartGame.js";
import GameMultiplayerContainer from "./components/Game/Multiplayer.js";
import GameLocalContainer from "./components/Game/Local.js";

// Tournament
import TournamentsContainer from "./components/Tournaments/TournamentsContainer.js";
import CreateTournamentContainer from "./components/Tournaments/CreateTournamentContainer.js";
import SubscribeTournamentContainer from "./components/Tournaments/SubscribeTournamentContainer.js";
import ManageTournamentContainer from "./components/Tournaments/ManageTournamentContainer.js";
import GetTournamentContainer from "./components/Tournaments/GetTournamentContainer.js";

// Profile
import ShortProfileMenu from "./components/Profile/ShortProfileMenu.js";
import ProfileContainer from "./components/Profile/Container.js";
import ProfileNotFound from "./components/Profile/NotFound.js";
import ProfileEditContainer from "./components/Profile/EditContainer.js";
import ProfileEditForm from "./components/Profile/EditForm.js";
import EditButton from "./components/Profile/EditButton.js";
import ProfileGameHistoryContainer from "./components/Profile/Game/History/Container.js";

// Chats
import TypeBar from "./components/Chats/TypeBar.js";
import ChatsContainer from "./components/Chats/ChatsContainer.js";
import ChatsMessage from "./components/Chats/Message.js";
import ChatFriendNotFound from "./components/Chats/FriendNotFound.js";

// Friends
import FriendsLink from "./components/NavLinks/FriendsLink.js";
import FriendWaitingItem from "./components/Friends/FriendWaitingItem.js";
import FriendEmptyWaitingArray from "./components/Friends/FriendEmptyWaitingArray.js";
import FriendItem from "./components/Friends/FriendItem.js";
import AddFriendButton from "./components/Friends/AddFriendButton.js";
import RemoveFriendButton from "./components/Friends/RemoveFriendButton.js";
import FriendsContainer from "./components/Friends/FriendsContainer.js";
import FormAddFriend from "./components/Friends/FormAddFriend.js";

// Blocks
import BlockUserButton from "./components/Blocks/BlockUserButton.js";
import BlockLink from "./components/NavLinks/BlockLink.js";
import BlockItem from "./components/Blocks/BlockItem.js";
import BlocksContainer from "./components/Blocks/BlocksContainer.js";
import FormAddBlock from "./components/Blocks/FormAddBlock.js";
import RemoveBlockButton from "./components/Blocks/RemoveBlockButton.js";

// Private Messages
import PmItem from "./components/Chats/PmItem.js";

// Form
import CustomInput from "./components/Form/CustomInput.js";
import NavBtn from "./components/Form/NavBtn.js";

// Menu
import MenuBtn from "./components/MenuBtn.js";
import {initAuth} from "./auth.js";

registerComponent("nav-link", NavLink);
registerComponent("login-button", LoginButton);
registerComponent("login-form", LoginForm);
registerComponent("register-form", RegisterForm);
registerComponent("logout-button", LogoutButton);

registerComponent("main-container", MainContainer);
registerComponent("short-profile-menu", ShortProfileMenu);
registerComponent("type-bar", TypeBar);
registerComponent("nav-container", NavContainer);
registerComponent("pm-item", PmItem);
registerComponent("new-friends-item", FriendsLink);
registerComponent("block-link", BlockLink);
registerComponent("friend-waiting-item", FriendWaitingItem);
registerComponent("friend-empty-waiting-array", FriendEmptyWaitingArray);
registerComponent("friend-item", FriendItem);
registerComponent("add-friend-button", AddFriendButton);
registerComponent("remove-friend-button", RemoveFriendButton);
registerComponent("remove-block-button", RemoveBlockButton);
registerComponent("block-friend-button", BlockUserButton);
registerComponent("block-user-button", BlockUserButton);
registerComponent("friends-container", FriendsContainer);
registerComponent("blocks-container", BlocksContainer);
registerComponent("form-add-friend", FormAddFriend);
registerComponent("form-add-block", FormAddBlock);
registerComponent("block-item", BlockItem);
registerComponent("profile-container", ProfileContainer);
registerComponent("profile-not-found", ProfileNotFound);
registerComponent("profile-edit-container", ProfileEditContainer);
registerComponent("profile-edit-form", ProfileEditForm);
registerComponent("edit-button", EditButton);
registerComponent("chats-container", ChatsContainer);
registerComponent("chats-message", ChatsMessage);
registerComponent("game-multiplayer-container", GameMultiplayerContainer);
registerComponent("game-local-container", GameLocalContainer);
registerComponent("game-link", GameLink);
registerComponent("start-game", StartGame);
registerComponent("custom-input", CustomInput);
registerComponent("tournaments-container", TournamentsContainer);
registerComponent("createtournament-container", CreateTournamentContainer);
registerComponent(
	"subscribe-tournament-container",
	SubscribeTournamentContainer
);
registerComponent("manage-tournament-container", ManageTournamentContainer);
registerComponent("get-tournament-container", GetTournamentContainer);
registerComponent(
	"profile-game-history-container",
	ProfileGameHistoryContainer
);

registerComponent("a2f-form-enable", A2FFormEnable);
registerComponent("a2f-form-disable", A2FFormDisable);
registerComponent("a2f-form", A2FForm);

registerComponent("menu-btn", MenuBtn);
registerComponent("menu-link", MenuLink);
registerComponent("nav-btn", NavBtn);

registerComponent("chats-friend-not-found", ChatFriendNotFound);

function getWindowLocation() {
	const path = window.location.pathname;
	const search = window.location.search;
	const params = {};
	search
		.substring(1)
		.split("&")
		.forEach((param) => {
			const [key, value] = param.split("=");
			params[key] = value;
		});

	return {path, params}
}

async function initApp() {
	const { path, params } = getWindowLocation()

	console.info("Initialize store");
	await initStore();
	console.info("Initialize router");
	await initRouter(path, params);
	console.info("Initialize auth");

	const nextPath = await initAuth();
	await loadPage(nextPath);
}

window.addEventListener("load", async () => {
	console.info("LOAD event");
	// const path = window.location.pathname;
	// const search = window.location.search;
	// const params = {};
	// search
	// 	.substring(1)
	// 	.split("&")
	// 	.forEach((param) => {
	// 		const [key, value] = param.split("=");
	// 		params[key] = value;
	// 	});

	await initApp();

	// await initAccess(path);
});

window.addEventListener("popstate", async (e) => {
	e.preventDefault();
	console.info("POPSTATE event", e);
	const path = window.location.pathname;
	const search = window.location.search;
	console.log(`search: ${search}`);
	await loadPage(path, false);
});

document.refresh = () => loadPage(null, false);
