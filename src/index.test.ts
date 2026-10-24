import main from "./index";

describe("TypeScript scaffold", () => {
  it("has no output when imported", () => {
    const log = jest.spyOn(console, "log").mockImplementation(() => undefined);
    try {
      jest.isolateModules(() => jest.requireActual("./index"));
      expect(log).not.toHaveBeenCalled();
    } finally {
      log.mockRestore();
    }
  });

  it("prints the scaffold status when invoked", () => {
    const log = jest.spyOn(console, "log").mockImplementation(() => undefined);
    try {
      main();
      expect(log).toHaveBeenCalledWith(
        "Project-ELM369 scaffold — replace with real entrypoint.",
      );
    } finally {
      log.mockRestore();
    }
  });
});
