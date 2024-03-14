import { html } from "../../html.js";
import { getData, setData } from "../../store.js";
import { loadPage } from "../../router.js";
import {postData} from "../../api.js";

export default (props) => {
	const user = getData("auth.user");
	return {
		template: html`
			<input type="file" id="avatar" accept="image/*" class="d-none" />
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh;overflow-y: auto">
					<menu-btn></menu-btn>
					<div
						class="d-block d-md-none pointer"
						style="
						color: white;
						font-size: 26px;
						padding-top: 25px;
						padding-right: 25px;
						padding-left: 25px;
					"
						id="menu_button">
						<i class="fa fa-bars"></i>
					</div>
					<div id="settings_container" class="d-cord-container">
						<div
							class="shadow-lg mt-5 m-md-5 ml-auto mr-auto"
							style="background-color:#171a1d;max-width:500px;padding:20px;border-radius:10px;color:#dfdfdf;">
							<div
								style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
								<div>
									<h3 class="text-white">Settings</h3>
									<h6>Edit your profile</h6>
								</div>
								<logout-button></logout-button>
							</div>
							<br />
							<div id="main_settings" class="">
									<div>
										<img
											src="${user.avatar}"
											style="width:80px; height:80px; border-radius:50%;cursor:pointer;"
											id="avatar_preview" />

										<input
											type="hidden"
											name="avatar"
											id="edit-profile-avatar-base64"
											class="form-control" />
									</div>
									<div class="mt-3">
										<custom-input
											id="edit-profile-username"
											icon="fa fa-user"
											type="text"
											required="yes"
											value=${user.username}
											>Username</custom-input
										>
									</div>
									<div class="mt-3">
										<custom-input
											id="edit-profile-password"
											icon="fa fa-lock"
											type="password"
											required="yes"
											>Password</custom-input
										>
									</div>
									<div class="mt-3">
										<custom-input
											id="edit-profile-confirm_password"
											icon="fa fa-lock"
											type="password"
											required="yes"
											>Confirm</custom-input
										>
									</div>
									<div class="text-right mt-3">
										<button class="btn btn-sm btn-light" id="save_edit">
											Save changes
										</button>
									</div>
									<br />
									<div
										class="mt-3 d-flex justify-content-between">
										<button
											type="button"
											class="btn btn-light"
											id="backtochat">
											Back to chat
										</button>
										<button
											type="button"
											class="btn btn-primary ${getData('auth.user.a2f_enabled') ? 'd-none' : ''}"
											id="setup2fa">
											Set up 2FA
										</button>
										<button
											type="button"
											class="btn btn-danger ${getData('auth.user.a2f_enabled') ? '' : 'd-none'}"
											id="setup2fa">
											Disable 2FA
										</button>
									</div>
							</div>
							<div id="2fa_settings" class="d-none">
								<a2f-form-enable class="${getData('auth.user.a2f_enabled') ? 'd-none' : ''}"></a2f-form-enable>
								<a2f-form-disable class="${getData('auth.user.a2f_enabled') ? '' : 'd-none'}"></a2f-form-disable>
							</div>
						</div>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#save_edit",
				event: "click",
				method: function () {
					console.log('test');
					const avatar = document.getElementById('edit-profile-avatar-base64').value;
					const username = document.querySelector('input#edit-profile-username').value;
					const password = document.querySelector('input#edit-profile-password').value;
					const confirm_password = document.querySelector('input#edit-profile-confirm_password').value;

					postData(
						`${process.env.BASE_URL}/me/update`,
						{
							avatar,
							username,
							password,
							confirm_password
						},
						"PATCH"
					).then((data) => {
						setData({
							auth: {
								user: data
							}
						});
					}).catch((err) => {
						let error = '';
						console.error(err)
						for (const [key, value] of Object.entries(err)) {
							error += `${value}\n`;
						}
						showToast(error);
					})
				}
			},
			{
				selector: "#mainContainer",
				event: "click",
				method: function (e) {
					if (
						!$(e.target).closest("#short-profile-menu").length &&
						!$(e.target).closest("#profile-menu").length
					) {
						$("#short-profile-menu").addClass("d-none");
					}
				},
			},
			{
				selector: "#menu_button",
				event: "click",
				method: function () {
					const navContainer =
						document.querySelector("#nav_container");
					if (navContainer) {
						navContainer.classList.remove("d-none");
					}
				},
			},
			{
				selector: "#avatar",
				event: "change",
				method: (e) => {
					const file = e.target.files[0];
					const reader = new FileReader();
					reader.onloadend = function () {
						document.getElementById("avatar_preview").src =
							reader.result;
						const canvas = document.createElement("canvas");
						const ctx = canvas.getContext("2d");
						const image = new Image();
						image.src = reader.result;
						image.onload = function () {
							canvas.width = 75;
							canvas.height = 75;
							ctx.drawImage(image, 0, 0, 75, 75);
							document.getElementById("edit-profile-avatar-base64").value =
								canvas.toDataURL();
						};
					};
					reader.readAsDataURL(file);
				},
			},
			{
				selector: "#avatar_preview",
				event: "click",
				method: () => {
					document.getElementById("avatar").click();
				},
			},
			{
				selector: "#backtochat",
				event: "click",
				method: () => {
					loadPage("/");
				},
			},
			{
				selector: "#setup2fa",
				event: "click",
				method: () => {
					const main = document.getElementById("main_settings");
					const _2fa = document.getElementById("2fa_settings");
					if (main.classList.contains("d-none")) {
						main.classList.remove("d-none");
						_2fa.classList.add("d-none");
					} else {
						main.classList.add("d-none");
						_2fa.classList.remove("d-none");
					}
				},
			},
		],
	};
};