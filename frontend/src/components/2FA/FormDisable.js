import { getUserInfo, postData } from "../../api.js";
import {html} from "../../html.js";
import { setData } from "../../store.js";

export default (props) => {
    const {qrcode, secret} = props;
    return {
        template: html`
			<div class="mt-3">
				<div class="alert alert-danger" role="alert">
					Are you sure you want to disable 2FA?
				</div>
				<br />
				<div
					class="mt-3 d-flex justify-content-between">
					<button
						type="button"
						class="btn btn-light"
						id="cancel_2fa">
						Cancel
					</button>
					<button
						type="button"
						class="btn btn-danger"
						id="disable_2fa">
						Disable
					</button>
				</div>
			</div>
        `,
        handlers: [
            {
                selector: '#disable_2fa',
                event: 'click',
                method: async function () {
                    await postData(`${process.env.BASE_URL}/authentication/disable-2fa`)
                    .then((response) => {
                        showToast(response.message);
                        setData({auth: getUserInfo()}, {reload: true});
                    })
                    .catch(error => {
                        console.log(error);
                    })
                }
            },
			{
				selector: "#cancel_2fa",
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
        ]
    };
}