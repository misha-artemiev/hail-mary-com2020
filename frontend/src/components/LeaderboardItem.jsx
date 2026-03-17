/**
 * LeaderboardItem.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * Displays a single line of the leaderboard.
 *
 * @param {Object} props
 * @param {string} props.username - The username of this user
 * @param {Number} props.count - The 'score' of the user in the given category
 * @param {Number} props.position - The place in the leaderboard of this user
 * @param {string} props.category - The category to score by
 * @param {Function} props.onClick - Click handler to navigate to user profile
 *
 * @returns {JSX.Element} a single line of the leaderboard
 */
export default function LeaderboardItem({
    username,
    count,
    position,
    category,
    onClick,
}) {
    /**
     * Converts the top three ranks to emojis (gold/silver/bronze medals)
     *
     * @returns {string} the emoji or position
     */
    const getRankEmoji = () => {
        switch (position) {
            case 0:
                return "\u{1F947}"; // Gold medal
            case 1:
                return "\u{1F948}"; // Silver medal
            case 2:
                return "\u{1F949}"; // Bronze medal
            default:
                return `${position + 1}.`;
        }
    };

    const generateLabel = () => {
        if (category === "reservations") {
            return <span>{count} reservations</span>;
        } else {
            return (
                <span>
                    {(count / 1000).toFixed(1)} kg CO<sub>2</sub> saved
                </span>
            );
        }
    };

    return (
        <div
            onClick={onClick}
            role="button"
            tabIndex={0}
            className="flex items-center justify-between
                       px-4 py-3 rounded-lg
                       bg-gray-50 border border-gray-100 cursor-pointer
                       hover:bg-green-50 hover:border-green-200 transition-colors"
        >
            <div className="flex items-center gap-3">
                <span className="text-lg w-8 text-center">
                    {getRankEmoji()}
                </span>
                <span className="font-semibold text-gray-800">{username}</span>
            </div>
            <span className="font-bold text-green-700">{generateLabel()}</span>
        </div>
    );
}
