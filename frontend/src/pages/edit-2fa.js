import { getUserInfo } from "../api.js";
import {html} from "../html.js";
import { getData } from "../store.js";

export default async () => {
    let qrcode = {
        qrcode: '',
        secret: ''
    };
    if (!getData('auth.user.a2f_enabled'))
    {
        qrcode = await fetch(`${process.env.BASE_URL}/authentication/request-code`, {
            credentials: "include"
        })
        .then(async (response) => {
            return await response.json();
        })
    }
    return html`
        <div class="d-flex" style="background: #252a2f" id="mainContainer">
            <nav-container></nav-container>
            <div style="width: 100%; height: 100svh">
				<menu-btn></menu-btn>
                <div
                    id="profile_container"
                    class="d-cord-container"
                    style="overflow-y: auto; padding:20px;"
                >
                    <a2f-form-enable qrcode="${qrcode.qrcode}" secret="${qrcode.secret}" class="${getData('auth.user.a2f_enabled') ? 'd-none' : ''}"></a2f-form-enable>
                    <a2f-form-disable class="${getData('auth.user.a2f_enabled') ? '' : 'd-none'}"></a2f-form-disable>
                </div>
            </div>
        </div>
    `
}