import { html } from "../../html.js";

export default (props) => {
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div
                        id="profile_container"
                        class="d-cord-container"
                        style="overflow-y: auto; padding:20px;"
                    >
                        <div
                            class="list-group"
                            style="margin: 25px; border-radius: 15px">
                            <h2 style="color: white;">Utilisateur introuvable</h2>
                    	</div>
					</div>
				</div>
			</div>
		`,
	};
};