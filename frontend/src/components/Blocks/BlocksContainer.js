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
                        <div
                            class="list-group"
                            style="margin: 25px; border-radius: 15px">
                            <div
                                class="d-flex justify-content-between align-items-center list-group-item">
                                <div class="d-flex align-items-center">
                                    <strong class="d-block">Utilisateur bloqués</strong>
                                </div>
								<form-add-block></form-add-block>
                            </div>
							${((getData("blocks") || []).map(block => {
								return html`
									<block-item
										name="${block.receiver.username}"
										avatar="${block.receiver.avatar}"
									/>`;
								})
							)}
                        </div>
				</div>
			</div>
		`,
	};
};
