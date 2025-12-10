import { Header } from "@/components/header";
import { ChatContainer } from "@/components/chat";

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      <main className="flex-1 overflow-hidden">
        <div className="h-full max-w-4xl mx-auto bg-white shadow-sm">
          <ChatContainer />
        </div>
      </main>
    </div>
  );
}
