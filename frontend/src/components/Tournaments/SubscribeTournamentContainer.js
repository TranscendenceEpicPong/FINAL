import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import {tournaments} from "../../api.js";

export default (props) => {
	const user = getData("auth.user");
	const { tournament: tournament_str } = props
	const tournament = JSON.parse(tournament_str)
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100vh; overflow-y: auto">
					<menu-btn></menu-btn>
					<div
						class="shadow-lg mt-5 m-md-5 ml-auto mr-auto"
						style="background-color:#171a1d;max-width:500px;padding:20px;border-radius:10px;color:#dfdfdf;">
						<div
							style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
							<div>
								<h3 class="text-white">Subscribe</h3>
								<h6>
									Enter your alias and subscribe to the
									tournament
								</h6>
							</div>
						</div>
						<br />
						<div>
							<div class="mt-3">
								<custom-input
									icon="fa fa-pencil"
									type="text"
									required="yes"
									value="${user.username}"
									id="alias"
								>
									My alias
								</custom-input>
							</div>
							<br />
							<div class="mt-3 d-flex justify-content-between">
								<button
									type="button"
									class="btn btn-light"
									id="cancel">
									Cancel
								</button>
								<button
									type="button"
									class="btn btn-primary"
									id="subscribe">
									Register
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#cancel",
				event: "click",
				method: function () {
					loadPage("/tournaments");
				},
			},
			{
				selector: "#subscribe",
				event: "click",
				method: async function () {
					const id = tournament.id;
					const alias = document.querySelector('input[id="alias"]').value;
					try {
						await tournaments.join({id, alias});
						await loadPage();
					} catch (e) {
						showToast(`ERROR ${e.error ?? e}`);
						console.error(e);
					}				},
			},
		],
	};
};
