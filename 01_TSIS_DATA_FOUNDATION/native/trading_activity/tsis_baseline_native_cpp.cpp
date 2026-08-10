#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <unordered_map>
#include <vector>

namespace py = pybind11;
constexpr double NANV = std::numeric_limits<double>::quiet_NaN();

struct GroupData {
    std::vector<double> values[4];
    std::vector<double> durations;
    std::int64_t max_available = std::numeric_limits<std::int64_t>::min();
    std::int64_t observations = 0;
};

struct Summary {
    bool available = false;
    bool zero_dominated = false;
    bool duration_available = false;
    std::int64_t observations = 0;
    std::int64_t max_available = std::numeric_limits<std::int64_t>::min();
    double distribution[48];
    double duration_median = NANV;
    std::vector<double> sorted[4];
    Summary() { std::fill(std::begin(distribution), std::end(distribution), NANV); }
};

double median_sorted(const std::vector<double>& values) {
    const auto n = values.size();
    if (!n) return NANV;
    if (n % 2) return values[n / 2];
    return (values[n / 2 - 1] + values[n / 2]) / 2.0;
}

double nearest_rank(const std::vector<double>& values, std::size_t begin, double p) {
    const auto n = values.size() - begin;
    if (!n) return NANV;
    auto rank = static_cast<std::size_t>(std::ceil(p * static_cast<double>(n)));
    rank = std::max<std::size_t>(1, rank);
    return values[begin + rank - 1];
}

void summarize_field(std::vector<double>& values, double* out) {
    std::sort(values.begin(), values.end());
    const auto n = values.size();
    const auto positive_begin_it = std::upper_bound(values.begin(), values.end(), 0.0);
    const auto positive_begin = static_cast<std::size_t>(positive_begin_it - values.begin());
    const auto positives = n - positive_begin;
    const auto zeros = static_cast<std::size_t>(std::count(values.begin(), values.end(), 0.0));
    out[0] = static_cast<double>(n);
    out[1] = static_cast<double>(zeros);
    out[2] = static_cast<double>(positives);
    out[3] = n ? static_cast<double>(zeros) / static_cast<double>(n) : NANV;
    out[4] = median_sorted(values);
    if (positives >= 10) {
        std::vector<double> positive(values.begin() + static_cast<std::ptrdiff_t>(positive_begin), values.end());
        const auto center = median_sorted(positive);
        out[5] = center;
        std::vector<double> deviations;
        deviations.reserve(positive.size());
        for (double value : positive) deviations.push_back(std::abs(value - center));
        std::sort(deviations.begin(), deviations.end());
        out[6] = median_sorted(deviations);
        out[7] = nearest_rank(values, positive_begin, 0.50);
    }
    if (positives >= 20) out[8] = nearest_rank(values, positive_begin, 0.75);
    if (positives >= 50) out[9] = nearest_rank(values, positive_begin, 0.90);
    if (positives >= 100) out[10] = nearest_rank(values, positive_begin, 0.95);
    if (positives >= 500) out[11] = nearest_rank(values, positive_begin, 0.99);
}

py::dict compute(
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> prior_session,
    py::array_t<std::int16_t, py::array::c_style | py::array::forcecast> prior_minute,
    py::array_t<std::int16_t, py::array::c_style | py::array::forcecast> prior_window,
    py::array_t<std::uint8_t, py::array::c_style | py::array::forcecast> prior_calculated,
    py::array_t<double, py::array::c_style | py::array::forcecast> prior_values,
    py::array_t<std::int64_t, py::array::c_style | py::array::forcecast> prior_available,
    py::array_t<std::int16_t, py::array::c_style | py::array::forcecast> current_minute,
    py::array_t<std::int16_t, py::array::c_style | py::array::forcecast> current_window,
    py::array_t<double, py::array::c_style | py::array::forcecast> current_values,
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> candidate_start,
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> candidate_first,
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> candidate_last,
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> candidate_sessions,
    py::array_t<std::int32_t, py::array::c_style | py::array::forcecast> candidate_minimum,
    std::int32_t evaluation_session
) {
    const auto ps = prior_session.unchecked<1>();
    const auto pm = prior_minute.unchecked<1>();
    const auto pw = prior_window.unchecked<1>();
    const auto pc = prior_calculated.unchecked<1>();
    const auto pv = prior_values.unchecked<2>();
    const auto pa = prior_available.unchecked<1>();
    const auto cm = current_minute.unchecked<1>();
    const auto cw = current_window.unchecked<1>();
    const auto cv = current_values.unchecked<2>();
    const auto starts = candidate_start.unchecked<1>();
    const auto firsts = candidate_first.unchecked<1>();
    const auto lasts = candidate_last.unchecked<1>();
    const auto sessions = candidate_sessions.unchecked<1>();
    const auto minimums = candidate_minimum.unchecked<1>();
    if (pv.shape(1) != 5 || cv.shape(1) != 5) throw std::runtime_error("values must have five columns");
    const py::ssize_t n_current = cm.shape(0);
    const py::ssize_t n_candidates = starts.shape(0);
    const py::ssize_t n_output = n_current * n_candidates;

    py::array_t<std::int8_t> state(n_output), duration_state(n_output), zero_dominated(n_output);
    py::array_t<std::int32_t> reference_sessions(n_output), reference_observations(n_output), first_reference(n_output), last_reference(n_output);
    py::array_t<std::int64_t> max_available(n_output);
    py::array_t<double> distributions({n_output, py::ssize_t(48)}), percentiles({n_output, py::ssize_t(4)}), ratios({n_output, py::ssize_t(3)}), durations({n_output, py::ssize_t(2)});
    auto os = state.mutable_unchecked<1>(); auto ods = duration_state.mutable_unchecked<1>(); auto oz = zero_dominated.mutable_unchecked<1>();
    auto ors = reference_sessions.mutable_unchecked<1>(); auto oro = reference_observations.mutable_unchecked<1>();
    auto of = first_reference.mutable_unchecked<1>(); auto ol = last_reference.mutable_unchecked<1>(); auto oma = max_available.mutable_unchecked<1>();
    auto od = distributions.mutable_unchecked<2>(); auto op = percentiles.mutable_unchecked<2>(); auto orat = ratios.mutable_unchecked<2>(); auto odur = durations.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < n_output; ++i) {
        os(i)=0; ods(i)=0; oz(i)=-1; oro(i)=0; oma(i)=std::numeric_limits<std::int64_t>::min();
        for(int j=0;j<48;++j) od(i,j)=NANV;
        for(int j=0;j<4;++j) op(i,j)=NANV;
        for(int j=0;j<3;++j) orat(i,j)=NANV;
        odur(i,0)=NANV; odur(i,1)=NANV;
    }

    py::gil_scoped_release release;
    for (py::ssize_t candidate = 0; candidate < n_candidates; ++candidate) {
        std::unordered_map<std::int32_t, GroupData> groups;
        groups.reserve(2048);
        for (py::ssize_t i = 0; i < ps.shape(0); ++i) {
            if (!pc(i) || ps(i) < starts(candidate) || ps(i) >= evaluation_session) continue;
            const std::int32_t key = static_cast<std::int32_t>(pm(i)) * 1000 + static_cast<std::int32_t>(pw(i));
            auto& group = groups[key];
            ++group.observations;
            if (pa(i) != std::numeric_limits<std::int64_t>::min()) group.max_available = std::max(group.max_available, pa(i));
            for (int field = 0; field < 4; ++field) if (!std::isnan(pv(i, field))) group.values[field].push_back(pv(i, field));
            if (!std::isnan(pv(i, 4))) group.durations.push_back(pv(i, 4));
        }
        std::unordered_map<std::int32_t, Summary> summaries;
        summaries.reserve(groups.size());
        for (auto& pair : groups) {
            auto& summary = summaries[pair.first];
            auto& group = pair.second;
            summary.observations = group.observations;
            summary.max_available = group.max_available;
            bool enough = sessions(candidate) >= minimums(candidate) && group.observations >= minimums(candidate);
            for (int field = 0; field < 4; ++field) enough = enough && group.values[field].size() >= static_cast<std::size_t>(minimums(candidate));
            if (!enough) continue;
            summary.available = true;
            for (int field = 0; field < 4; ++field) {
                summarize_field(group.values[field], summary.distribution + field * 12);
                summary.sorted[field] = std::move(group.values[field]);
            }
            summary.zero_dominated = summary.distribution[3] >= 0.80;
            if (group.durations.size() >= static_cast<std::size_t>(minimums(candidate))) {
                std::sort(group.durations.begin(), group.durations.end());
                summary.duration_available = true;
                summary.duration_median = median_sorted(group.durations);
            }
        }
        #pragma omp parallel for schedule(static)
        for (std::int64_t i = 0; i < static_cast<std::int64_t>(n_current); ++i) {
            const auto output_index = static_cast<py::ssize_t>(i) * n_candidates + candidate;
            ors(output_index)=sessions(candidate); of(output_index)=firsts(candidate); ol(output_index)=lasts(candidate);
            const std::int32_t key = static_cast<std::int32_t>(cm(i)) * 1000 + static_cast<std::int32_t>(cw(i));
            auto found = summaries.find(key);
            if (found == summaries.end()) continue;
            const auto& summary = found->second;
            oro(output_index)=static_cast<std::int32_t>(summary.observations); oma(output_index)=summary.max_available;
            if (!summary.available) continue;
            os(output_index)=summary.zero_dominated ? 2 : 1; oz(output_index)=summary.zero_dominated ? 1 : 0;
            ods(output_index)=summary.duration_available ? 1 : 0;
            for(int j=0;j<48;++j) od(output_index,j)=summary.distribution[j];
            for(int field=0;field<4;++field) {
                const double value=cv(i,field);
                if(!std::isnan(value)) {
                    const auto& sorted=summary.sorted[field];
                    op(output_index,field)=static_cast<double>(std::upper_bound(sorted.begin(),sorted.end(),value)-sorted.begin())/static_cast<double>(sorted.size());
                }
            }
            for(int field=0;field<3;++field) if(!std::isnan(cv(i,field))) orat(output_index,field)=std::log((cv(i,field)+1.0)/(summary.distribution[field*12+4]+1.0));
            if(summary.duration_available) {
                odur(output_index,0)=summary.duration_median;
                if(!std::isnan(cv(i,4))) odur(output_index,1)=std::log((summary.duration_median+1.0)/(cv(i,4)+1.0));
            }
        }
    }
    py::gil_scoped_acquire acquire;
    py::dict result;
    result["state"]=state; result["duration_state"]=duration_state; result["zero_dominated"]=zero_dominated;
    result["reference_sessions"]=reference_sessions; result["reference_observations"]=reference_observations;
    result["first_reference"]=first_reference; result["last_reference"]=last_reference; result["max_available"]=max_available;
    result["distributions"]=distributions; result["percentiles"]=percentiles; result["ratios"]=ratios; result["durations"]=durations;
    return result;
}

PYBIND11_MODULE(tsis_baseline_native_cpp, module) {
    module.doc() = "TSIS Trading Activity PIT baseline native kernel";
    module.def("compute", &compute);
}
