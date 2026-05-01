import { Link } from 'react-router-dom';
import { Anchor, Home } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center">
        <div className="text-8xl font-extrabold mb-4" style={{ color: 'var(--accent)' }}>404</div>
        <Anchor size={40} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text)' }}>Stránka nenalezena</h2>
        <p className="mb-8" style={{ color: 'var(--text-muted)' }}>
          Tato stránka neexistuje nebo byla přesunuta.
        </p>
        <Link to="/">
          <Button className="gap-2"><Home size={16} /> Zpět na úvod</Button>
        </Link>
      </div>
    </div>
  );
}
