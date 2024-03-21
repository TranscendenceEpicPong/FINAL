import { getUserInfo, postData } from "../../api.js";
import {html} from "../../html.js";
import { getData, setData } from "../../store.js";
import {logout}  from "../../auth.js";

export default async (props) => {
    let getqrcode = {
        qrcode: '',
        secret: ''
    };
    if (!getData('auth.user.a2f_enabled'))
    {
        getqrcode = await fetch(`${process.env.BASE_URL}/authentication/request-code`, {
            credentials: "include"
        })
        .then(async (response) => {
            return await response.json();
        })
    }
    const qrcode = getqrcode.qrcode;
    const secret = getqrcode.secret;
    return {
        template: html`
            <form id="form-enabling-a2f">
                <img
                src="${qrcode}" id="qrcode-2fa" alt="QRCode"
                width="200" />
                <div class="mt-3">
                    <custom-input
                        icon="fa fa-lock"
                        type="text"
                        required="yes"
                        readonly="yes"
                        value="${secret}"
                        >Secret</custom-input
                    >
                </div>
                <div class="mt-3">
                    <custom-input
                        icon="fa fa-qrcode"
                        type="password"
                        required="yes"
                        id="code"
                        >Enter 6 digit code</custom-input
                    >
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
                        class="btn btn-primary"
                        id="setup2fa">
                        Enable
                    </button>
                </div>
            </form>
        `,
        handlers: [
            {
                selector: '#setup2fa',
                event: 'click',
                method: async function () {
                    const form = document.getElementById('form-enabling-a2f');
                    const data = new FormData(form);
                    const reqBody = Object.fromEntries(data);

                    await postData(`${process.env.BASE_URL}/authentication/enable-2fa`,
                        reqBody
                    )
                    .then((response) => {
                        showToast(response.message);
                        setData({auth: getUserInfo()}, {reload: true});
                        logout();
                    })
                    .catch(error => {
                        showToast(error.message);
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