/**
 * Skeleton Loader - Visual placeholder while content loads
 * 
 * WHY: Instead of showing "Loading..." text, show the shape
 * of content that will appear. Better perceived performance.
 */

import './Skeleton.css';

export default function Skeleton({ 
  type = 'text',  // text, card, circle, stat
  count = 1,      // How many skeleton items
  height,         // Custom height
  width           // Custom width
}) {
  const skeletons = Array(count).fill(0);
  
  return (
    <>
      {skeletons.map((_, i) => (
        <div 
          key={i}
          className={`skeleton skeleton-${type}`}
          style={{ height, width }}
        />
      ))}
    </>
  );
}
