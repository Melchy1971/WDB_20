import { apiGet } from "./client";

export type FilesystemEntry = {
  name: string;
  path: string;
  is_dir: boolean;
};

export type FilesystemBrowseResponse = {
  current_path: string;
  parent_path: string | null;
  entries: FilesystemEntry[];
};

export function browseFilesystem(path?: string): Promise<FilesystemBrowseResponse> {
  const query = path !== undefined && path !== "" ? `?path=${encodeURIComponent(path)}` : "";
  return apiGet<FilesystemBrowseResponse>(`/filesystem/browse${query}`);
}
