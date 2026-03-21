/**
 * Modal.jsx
 */

import React from "react";

export default function Modal({ isOpen, onClose, title, children, maxWidth = "max-w-md" }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className={`bg-white rounded-lg shadow-xl w-full ${maxWidth} p-6`} onClick={(e) => e.stopPropagation()}>
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
