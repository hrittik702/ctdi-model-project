import React from 'react';

/**
 * Standardized Section Heading with Section-Aware Scroll Identity attributes.
 * Displays exclusively the clean, prominent section title.
 */
export default function SectionHeading({
  id,
  title,
  shortTitle = null,
  icon = null,
  action = null,
  topMargin = true,
  className = ""
}) {
  return (
    <div 
      data-section-id={id}
      data-section-title={shortTitle || title}
      data-section-icon={icon}
      data-section-heading="true"
      className={`transition-opacity duration-200 motion-reduce:transition-none pb-2 flex items-center justify-between gap-3 select-none ${className}`}
    >
      <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-[#F4F4F5]">
        {title}
      </h2>
      {action && (
        <div className="flex items-center gap-2 shrink-0">
          {action}
        </div>
      )}
    </div>
  );
}
