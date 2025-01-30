"use client";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { useMutation } from "@tanstack/react-query";

import ChatInput from "@/components/chat/ChatInput";
import ChatMessages from "@/components/chat/ChatMessages";
import UserMenu from "@/components/user/UserMenu";
import { api } from "@/api";

import type { DocumentPayload, DocumentType } from "@/api/wallstr-sdk";

export default function AppPage() {
  const router = useRouter();

  const { mutate, isPending } = useMutation({
    mutationFn: async ({ message, attachedFiles }: { message: string; attachedFiles: File[] }) => {
      const { data } = await api.chat.createChat({
        body: {
          message: message.trim() || null,
          documents: attachedFiles.map(
            (f): DocumentPayload => ({
              filename: f.name,
              doc_type: getDocumentType(f),
            }),
          ),
        },
        throwOnError: true,
      });

      Promise.all([
        data.pending_documents.map(async (document) => {
          const file = attachedFiles.find((file) => file.name === document.filename);
          if (!file) return;

          const response = await fetch(document.presigned_url, {
            method: "PUT",
            body: file,
          });

          if (response.ok) {
            await api.documents.markDocumentUploaded({ path: { id: document.id } });
          }
        }),
      ]);
      return data;
    },
    onSuccess: (data) => {
      router.push(`/app/${data.chat.slug}`);
    },
  });

  const createChat = useCallback(
    async (message: string, attachedFiles: File[]) => {
      mutate({
        message,
        attachedFiles,
      });
    },
    [mutate],
  );

  return (
    <div className="flex flex-col grow">
      <header className="border-b border-base-300 bg-base-100">
        <div className="flex h-16 items-center justify-between px-4">
          <h1 className="text-xl font-semibold">WallStr.chat</h1>
          <UserMenu />
        </div>
      </header>

      <main className="flex-1 overflow-hidden bg-base-200">
        <div className="flex h-full flex-col">
          <ChatMessages />
          <ChatInput onSubmit={createChat} isPending={isPending} />
        </div>
      </main>
    </div>
  );
}

const getDocumentType = (file: File): DocumentType => {
  switch (file.type) {
    case "application/pdf":
      return "pdf";
    default:
      throw new Error("Unsupported file type");
  }
};
