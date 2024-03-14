import {html} from "../../html.js";
import { makeRequestFriend } from "../../utils/friends.js";

export default (props) => {
    return {
        template: html`
            <form id="form-add-friend" class="d-flex" action="hello">
                <div>
					<custom-input icon="fa fa-user" type="text" required="yes" id="username">Enter username</custom-input>
                </div>
                <div>
                    <button
                        id="btn-add-friend"
                        class="btn btn-light btn-sm"
                        style="width: 100%; height: 100%"
                        type="submit"
                    >
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </form>
        `,
        handlers: [
            {
                selector: "#btn-add-friend",
                event: "click",
                method: (e) => {
                    const form = document.getElementById("form-add-friend");
                    const formData = new FormData(form);
                    const username = formData.get("username");
                    makeRequestFriend(username, 'add');
                }
            }
        ]
    };
}