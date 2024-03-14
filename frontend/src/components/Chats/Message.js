import {html} from "../../html.js";

export default (props) => {
    const {username, avatar, textContent} = props;
    function isOnlyEmoji(str) {
        const emojiRegex = /(\p{Emoji_Presentation}|\p{Extended_Pictographic})/gu;
        const cleanString = str.replace(emojiRegex, "");
        const onlySpaces = cleanString.trim().length === 0;
        return onlySpaces && str.length > 0;
    }
    return {
        template: html`
            <div class="text-white mt-3">
                <div class="d-flex">
                    <img
                        src="${avatar}"
                        class="rounded-circle img-fluid"
                        style="width: 40px; height: 40px" />
                    <div class="ml-2">
                        <h6 class="card-title mb-0">
                            ${username}
                        </h6>
                        <p
                            class="card-text"
                            style="color: #dfdfdf; ${isOnlyEmoji(textContent) ? "font-size: 40px" : ""}">
                            ${
                                textContent.includes("[join-game]") ?
                                    html`<div class="fight-widget">
    <h5>New challenge!</h5>
    <p>Your friend challenged you to a fight!</p>
</div>` : textContent
                            }
                        </p>
                    </div>
                </div>
            </div>
        `,
    };
}