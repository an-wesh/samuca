import Sidebar from "./Sidebar";

export default function AppLayout({ children }) {
  return (
    <div className="flex h-screen bg-[#050505] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto p-4">{children}</main>
    </div>
  );
}
