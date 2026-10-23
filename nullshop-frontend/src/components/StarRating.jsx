import { useState } from 'react';
import { Star } from 'lucide-react';

export default function StarRating({ rating = 0, onChange, readonly = false }) {

  const [hover, setHover] = useState(0);

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {

        const isFilled = hover > 0 ? star <= hover : star <= rating;

        return (
          <button
            key={star}
            type="button"
            disabled={readonly}
            onClick={() => {
              if (!readonly && onChange) {onChange(star)};
            }}
            onMouseEnter={() => {
              if (!readonly) {setHover(star)}
            }}
            onMouseLeave={() => {
              if (!readonly) {setHover(0)}
            }}
            className = {readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110 transition-transform'}
          >
            <Star
              className={`w-5 h-5 transition-colors ${
                isFilled ? 'fill-amber-400 text-amber-400' : 'text-slate-300'
              }`}
            />
          </button>
        );
      })}
    </div>
  );
}