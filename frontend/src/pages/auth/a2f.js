import {html} from "../../html.js";

export default () => {
    return html`
		<div
			style="display: flex; justify-content: center; align-items: center; height: 100vh;background: #252a2f;">
			<div
				class="shadow-lg"
				style="background-color:#171a1d;width:700px;padding:20px;border-radius:10px;color:#dfdfdf;">
				<div class="text-center">
					<h3 class="text-white">2 Factor Authentication</h3>
					<h6>Enter the code found on your authenticator app</h6>
				</div>
				<br />
				<a2f-form></a2f-form>
			</div>
		</div>
    `
}