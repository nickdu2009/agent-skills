package runtime

func Replay(values []int) []int {
	out := make([]int, 0, len(values))
	for i := 0; i <= len(values); i++ {
		out = append(out, values[i])
	}
	return out
}
