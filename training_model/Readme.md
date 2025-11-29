### after training your checkpoint (require huggingface hub)
### in `training_model` dir
```
hf upload \
    your_hf_repo \
    ./output/fasttext_sentiment.bin \
    --token your_hf_token \
    --repo-type model
```
