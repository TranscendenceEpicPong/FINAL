import { html } from "../../html.js";
import { getData } from "../../store.js";
import {loadPage} from "../../router.js";
import {setData} from "../../store.js";
import {getUserInfo, postData} from "../../api.js";
import { resetSockets } from "../../utils/socket.js";

export default (props) => {
	let displayProfileMenu = getData("displayProfileMenu") || "d-none";
	// set displayProfileMenu to "d-none" to hide the menu
	return {
		template: html`
			<div>
				<div id="short-profile-menu" class="${displayProfileMenu}">
					<div style="padding: 23px; background: #373737">
					</div>
					<div
						style="margin-right: 20px; margin-left: 20px; margin-top: -33px">
						<div>
							<img
								class="rounded-circle"
								style="
							width: 70px;
							height: 70px;
							border: 3px solid #131316;
						"
								src="${getData('auth.user.avatar')}" />
							<div
								data-toggle="tooltip"
								data-bss-tooltip=""
								style="
									position: absolute;
									margin-left: 49px;
									margin-top: -25px;
									border: 3px solid #131316;
									border-radius: 50%;
									width: 20px;
									height: 20px;
								"
								class="status-pill status-online"
								title="${getData('auth.user.status').charAt(0).toUpperCase() + getData('auth.user.status').slice(1)}"></div>
						</div>
					</div>
					<div
						class="text-white"
						style="
					margin: 20px;
					background: rgba(55, 55, 55, 0.31);
					padding: 10px;
					border-radius: 5px;
				">
						<h6
							class="font-weight-bolder"
							style="margin-bottom: 2px">
							${getData('auth.user.username').charAt(0).toUpperCase() + getData('auth.user.username').slice(1)}
						</h6>
						<h6 style="font-size: 13px">${getData('auth.user.username')}</h6>
						<div
							class="mt-3 mb-3"
							style="background: rgba(255, 255, 255, 0.27); height: 1px"></div>
						<h6
							class="text-uppercase font-weight-bolder"
							style="font-size: 12px">
							Current status
						</h6>
						<h6 style="font-size: 13px">Online</h6>
						<div
							class="mt-3 mb-3"
							style="background: rgba(255, 255, 255, 0.27); height: 1px"></div>
						<button
							id="profile-button"
							class="btn btn-light btn-block btn-sm"
							type="button">
							<i class="fa fa-user"></i>&nbsp;Profile
						</button>
						<button
							id="logout-button"
							class="btn btn-primary btn-block btn-sm"
							type="button">
							<i class="fa fa-sign-out"></i>&nbsp;Sign out
						</button>
					</div>
				</div>
				<div id="bottom-nav" style="margin-top: auto">
					<div id="profile-menu" style="position: relative">
						<h6
							style="
									margin-bottom: 0px;
									margin-left: 10px;
									position: absolute;
									display: flex;
									align-items: center;
									justify-content: center;
								">
							<img
								class="rounded-circle"
								style="width: 30px; height: 30px"
								src="${getData('auth.user.avatar')}" />&nbsp;${getData('auth.user.username').charAt(0).toUpperCase() + getData('auth.user.username').slice(1)}
						</h6>
						<div class="status-pill status-online"></div>
					</div>
					<i
						id="open-settings"
						class="fa fa-cog pointer"
						style="margin-left: auto; margin-right: 10px"
					></i>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#profile-menu",
				event: "click",
				method: function () {
					const menu = document.querySelector("#short-profile-menu");
					if (menu) {
						menu.classList.toggle("d-none");
					} else {
						console.error("Menu element not found in shadow DOM");
					}
				},
			},
			{
				selector: "#open-settings",
				event: "click",
				method: () => {
					loadPage('/edit');
				}
			},
			{
                selector: "#logout-button",
                event: "click",
                method: () => {
                    postData(`${process.env.BASE_URL}/authentication/logout`).then(async (response) => {
                        resetSockets();
                        setData({
                            auth: getUserInfo(),
                            friends: {
                                active: null,
                                waiting: null,
                            },
                            blocks: null,
                        });
                        loadPage("/auth/login");
                    })
                    .catch((error) => {
                        if (error.status === 401)
                            loadPage("/auth/login");
                    })
                }
            },
			{
				selector: "#profile-button",
				event: "click",
				method: () => {
					loadPage("/profile/" + getData("auth.user.username"));
				}
			}
		],
	};
};
