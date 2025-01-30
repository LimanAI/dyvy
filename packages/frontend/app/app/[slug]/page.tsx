"use client";
import { useParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";

import { api } from "@/api";
import ChatInput from "@/components/chat/ChatInput";
import ChatMessages from "@/components/chat/ChatMessages";
import UserMenu from "@/components/user/UserMenu";

export default function ChatPage() {
  const { slug } = useParams<{ slug: string }>();

  const { data: chat, isLoading } = useQuery({
    queryKey: ["/chat", slug],
    queryFn: async () => {
      const { data } = await api.chat.getChat({ path: { slug }, throwOnError: true });
      return data;
    },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: async ({ message, attachedFiles }: { message: string; attachedFiles: File[] }) => {
      // TODO: Implement sending message in existing chat
      console.log("Sending message:", message, attachedFiles);
    },
  });

  return (
    <div className="flex flex-col grow">
      <header className="border-b border-base-300 bg-base-100">
        <div className="flex h-16 items-center justify-between px-4">
          <h1 className="text-xl font-semibold">{isLoading ? "Loading..." : chat?.title || "New Chat"}</h1>
          <UserMenu />
        </div>
      </header>

      <main className="flex-1 overflow-hidden bg-base-200">
        <div className="flex h-full flex-col">
          <ChatMessages slug={slug} />
          <ChatInput onSubmit={(message, files) => mutate({ message, attachedFiles: files })} isPending={isPending} />
        </div>
      </main>
    </div>
  );
}
