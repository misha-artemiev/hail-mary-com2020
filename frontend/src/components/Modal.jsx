/**
 * Modal.jsx
 * @author Thomas Noakes
 */

import React from "react";

/**
 * A generic modal component with a dark overlay and centered content.
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether the modal is visible.
 * @param {Function} props.onClose - Callback when overlay is clicked.
 * @param {string} [props.title] - Optional title displayed in the modal header.
 * @param {React.ReactNode} props.children - Content to render inside the modal.
 * @param {string} [props.maxWidth="max-w-md"] - Tailwind max-width class.
 *
 * @returns {JSX.Element|null} the rendered modal, or null if not open.
 */
export default function Modal({
    isOpen,
    onClose,
    title,
    children,
    maxWidth = "max-w-md",
}) {
    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black/20 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className={`bg-white rounded-lg shadow-xl w-full ${maxWidth} p-6`}
                onClick={(e) => e.stopPropagation()}
            >
                {title && (
                    <h2 className="text-xl font-bold text-gray-800 mb-4">
                        {title}
                    </h2>
                )}
                {children}
            </div>
        </div>
    );
}
