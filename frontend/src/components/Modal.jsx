export default function Modal({ titulo, onClose, children }) {
  return (
    <div className="modal-fondo" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-cabeza">
          <h2>{titulo}</h2>
          <button type="button" className="secundario" onClick={onClose}>✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}