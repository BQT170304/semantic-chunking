import { NextRequest, NextResponse } from "next/server";

const SERVER_BASE_URL =
  process.env.UPLOAD_SERVER_BASE_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();

    const targetUrl = `${SERVER_BASE_URL}/upload`;

    const response = await fetch(targetUrl, {
      method: "POST",
      body: formData,
      headers: {
        // Don't set Content-Type, let fetch handle it for FormData
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend error:", errorText);
      return new NextResponse(errorText, {
        status: response.status,
        headers: {
          "Content-Type": "application/json",
        },
      });
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error("Error in API proxy route:", error);
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204, // No Content
    headers: {
      "Access-Control-Allow-Origin": "*", // Be more specific in production if needed
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization", // Adjust as per client's request headers
    },
  });
}
