import {html} from "../../html.js";
import { makeRequestFriend } from "../../utils/friends.js";

export default (props) => {
    const {username} = props;
    return {
        template: html`
            <button
                class="btn btn-success btn-sm mr-1"
                style="
                aspect-ratio: 1 / 1;
                width: 30px;
                height: 30px;
                "
            >
                <i class="fas fa-check"></i></button
            >
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: () => {
                    makeRequestFriend(username, 'accept');
                }
            }
        ]
    };
}