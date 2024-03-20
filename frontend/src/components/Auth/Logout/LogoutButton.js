import {html} from "../../../html.js";
import {resetStore, setData} from "../../../store.js";
import {loadPage} from "../../../router.js";
import {getUserInfo, postData} from "../../../api.js";
import { resetSockets } from "../../../utils/socket.js";
import {logout} from "../../../auth.js";

export default (props) => {
    return {
        template: html`
            <button class="btn btn-danger">
                <i class="fa fa-sign-out"></i> Logout
            </button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: logout
            }
        ]
    };
}