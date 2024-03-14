import { html } from "../../html.js";
import { loadPage } from "../../router.js";

export default (props) => {
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div
						id="chat_container"
						class="active_container cord-container">
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
									Ami introuvable
									</h6>
								</div>
								<hr style="background: #4b5157" />
							</div>
						</div>
					</div>
				</div>
			</div>
		`,
	};
};
